using BepInEx;
using BepInEx.Configuration;
using GameEvent;
using UCHBot.Comms.Requests;
using UCHBot.GlobalMods.Events;
using UCHBot.GlobalMods.Tools;
using UCHBot.Model.PathFinder;
using UnityEngine;
using Bounds = UCHBot.Model.Utils.Bounds;
using Vector2 = UCHBot.Model.Utils.Vector2;

namespace UCHBot.GlobalMods.Mods;

[BepInPlugin(nameof(PathFinderMod), nameof(PathFinderMod), "1.0.0")]
[BepInDependency(nameof(GlobalMod))]
public class PathFinderMod : BaseUnityPlugin, IGameEventListener
{
	private const int StartingPathNodeIndex = 0;
	private UCHPath _pathToExecute;
	private UCHPath _executedPath;
	private int _currentPathNodeIndex;
	private ConfigEntry<bool> _stepModeEnabled;
	private ConfigEntry<bool> _autoCorrectionEnabled;
	private ConfigEntry<float> _autoCorrectionFactor;
	private Vector2 _offset;
	private UCHPathNode _targetNode;
	private Character _character;
	private Rigidbody2D _rigidbody;

	private void Awake()
	{
		_autoCorrectionEnabled = Config.Bind("PathFinder", "AutoCorrection", false, "Enables/Disables the PathFinder AutoCorrection");
		_autoCorrectionFactor = Config.Bind("PathFinder", "AutoCorrectionFactor", 0.2f, "Set the strength of the AutoCorrection");
		_stepModeEnabled = Config.Bind("PathFinder", "StepMode", false, "Enables/Disables the PathFinder Step-by-Step Mode");
		_stepModeEnabled.Value = false;

		GameEventManager.ChangeListener<LevelResetEvent>(this, true);
		GameEventManager.ChangeListener<LevelDestroyedEvent>(this, true);

		CommunicationServer.Instance.RegisterMessageHandler<GeneratePathRequest>(GeneratePathRequest.RequestKey, null);
		CommunicationServer.Instance.RegisterMessageHandler<ExecuteGeneratedPathRequest>(ExecuteGeneratedPathRequest.RequestKey, ExecutePath);
		CommunicationServer.Instance.RegisterMessageHandler<ExecutedPathResults>(ExecutedPathResults.RequestKey, null);

		Logger.LogInfo($"Plugin {nameof(PathFinderMod)} is loaded!");
	}

	private void ExecutePath(ExecuteGeneratedPathRequest obj)
	{
		if (LobbyManager.instance.CurrentGameController == null)
			return;
		UCHTools.Message("Executing Path");
		_pathToExecute = obj.Paths[0];
	}

	private void Update()
	{
		if (Input.GetKeyDown(KeyCode.F9))
		{
			_stepModeEnabled.Value = !_stepModeEnabled.Value;
			UCHTools.Message("PathFinder StepMode is now " + (_stepModeEnabled.Value ? "Enabled" : "Disabled"));
			Time.timeScale = _stepModeEnabled.Value ? 0 : 1;
		}
		else if (Input.GetKeyDown(KeyCode.Return))
		{
			Time.timeScale = 1;
		}
		else if (Input.GetKeyDown(KeyCode.Escape))
		{
			StopExecution();
		}

		if (_targetNode != null)
		{
			Vector2 prevPos = _targetNode.Position + _offset;
			Vector3 pos = _character.transform.position;

			UnityEngine.Vector2 newPos = UnityEngine.Vector2.Lerp(
				new UnityEngine.Vector2(pos.x, pos.y),
				new UnityEngine.Vector2(prevPos.X, prevPos.Y),
				_autoCorrectionFactor.Value * Time.deltaTime
			);

			_character.transform.position = new Vector3(newPos.x, newPos.y, _character.transform.position.z);
		}
	}

	private void FixedUpdate()
	{
		if (_pathToExecute == null)
			return;

		if (_currentPathNodeIndex > _pathToExecute.Nodes.Count)
			return;

		if (_currentPathNodeIndex >= 0)
		{
			if (_currentPathNodeIndex == _pathToExecute.Nodes.Count)
			{
				CommunicationServer.Instance.Send(new ExecutedPathResults
				{
					Paths = new[] { _executedPath }
				});
				StopExecution();
			}
			else if (_currentPathNodeIndex < _pathToExecute.Nodes.Count)
			{
				if (_stepModeEnabled.Value)
				{
					Time.timeScale = 0;
					UCHTools.Message("Executing Step " + _currentPathNodeIndex);
				}

				UCHPathNode currentNode = _pathToExecute.Nodes[_currentPathNodeIndex];
				UCHTools.OverrideInputKeys(currentNode.Actions);



				if (_currentPathNodeIndex == 0)
				{
					_character = UCHTools.GetCharacters().Single();
					_rigidbody = _character.gameObject.GetComponent<Rigidbody2D>();
					Vector3 realPosition = _character.transform.position;
					Vector2 currentPosition = currentNode.Position;

					_offset = new Vector2(realPosition.x - currentPosition.X, realPosition.y - currentPosition.Y);
				}
				else if (_currentPathNodeIndex > 0)
				{
					UCHPathNode prevNode = _pathToExecute.Nodes[_currentPathNodeIndex - 1];

					Bounds bounds = _character.GetPlayerModel().Bounds;
					_executedPath.Nodes.Add(new UCHPathNode
					{
						Segment = prevNode.Segment,
						State = prevNode.State,	
						Actions = prevNode.Actions,
						Position = prevNode.Position,
						Velocity = prevNode.Velocity,
						RealPosition = new Vector2(bounds.CenterX, bounds.Bottom),
						RealVelocity = new Vector2(_rigidbody.velocity.x, _rigidbody.velocity.y),
						OnGround = _character.OnGround,
						OnWall = _character.GetField<bool>("onWall")
					});
				}
				{

					if (_autoCorrectionEnabled.Value)
					{
						if (_currentPathNodeIndex < _pathToExecute.Nodes.Count)
							_targetNode = _pathToExecute.Nodes[_currentPathNodeIndex];
					}
				}
			}
		}
		_currentPathNodeIndex++;
	}

	private void StopExecution()
	{
		_currentPathNodeIndex = _pathToExecute?.Nodes.Count ?? int.MaxValue;
		_targetNode = null;
		_stepModeEnabled.Value = false;
		InputWrapper.Clear();
	}

	public void handleEvent(GameEvent.GameEvent e)
	{
		switch (e)
		{
			// 4: Game is started
			case LevelResetEvent:
				StopExecution();
				//case StartPhaseEvent spe:
				//	if (spe.Phase == GameControl.GamePhase.PLAY)
				if (_pathToExecute == null)
				{
					UCHTools.Message("Sending PathFinder Request");

					CommunicationServer.Instance.Send(new GeneratePathRequest(
						LobbyManager.instance.CurrentGameController.GetLevelModel(),
						UCHTools.GetCharacters().Single().GetPlayerModel()
					));
				}
				else
				{
					UCHTools.Message("Using already generated path");
					_executedPath = new UCHPath();
					_currentPathNodeIndex = StartingPathNodeIndex;
				}

				break;

			case LevelDestroyedEvent:
				StopExecution();
				_pathToExecute = null;
				break;

		}
	}
}