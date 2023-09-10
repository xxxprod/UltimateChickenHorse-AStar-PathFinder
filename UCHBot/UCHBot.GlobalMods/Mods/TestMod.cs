using System.Collections;
using System.Threading.Tasks;
using BepInEx;
using GameEvent;
using UCHBot.GlobalMods.AutomatedTests;
using UCHBot.GlobalMods.Model;
using UCHBot.GlobalMods.Tools;
using UnityEngine;
using UnityEngine.TextCore;
using static GameState;
using static InputEvent;

namespace UCHBot.GlobalMods.Mods;

[BepInPlugin(nameof(TestMod), nameof(TestMod), "1.0.0")]
[BepInDependency(nameof(GlobalMod))]
public class TestMod : BaseUnityPlugin
{
	private TestScenario[] _testScenarios;
	private readonly HashSet<InputKey> _pressedKeys = new();
	private Character _character;
	private List<PlayerData> _playerData;
	private Vector3 _startPosition;

	private void Awake()
	{
		CommunicationServer.Instance.RegisterMessageHandler<TestScenario[]>("runTest", RunTest);
		CommunicationServer.Instance.RegisterMessageHandler<PlayerData[]>("testFinished", null);

		Logger.LogInfo($"Plugin {nameof(TestMod)} is loaded!");
	}

	private void RunTest(TestScenario[] testScenarios)
	{
		UCHTools.Log("RunTest called");

		if (_testScenarios != null)
		{
			UCHTools.Log($"Tests already running...");
			return;
		}

		_testScenarios = testScenarios.Flatten();
		_playerData = new List<PlayerData>();

		_ = RunTestScenarios();
	}

	private async Task RunTestScenarios()
	{
		try
		{
			foreach (IGrouping<string, TestScenario> testScenariosByLevel in _testScenarios.GroupBy(a => a.LevelName))
			{
				await UCHTools.LaunchLevel(testScenariosByLevel.Key, GameMode.FREEPLAY);

				GameEventManager.SendEvent(new FreePlayPlayerSwitchEvent(1, GameControl.GamePhase.PLAY));
				
				while (!UCHTools.GetCharacters().Any())
					await Task.Delay(100);

				_character = UCHTools.GetCharacters().Single();
				await Task.Delay(1000);
				_startPosition = _character.transform.position;


				foreach (TestScenario testScenario in testScenariosByLevel)
				{
					Debug.Log($"Starting Scenario {CreateScenarioName(testScenario)}");

					await StartCoroutineAsync(RunScenario(testScenario));

					ClearActions();

					await Task.Delay(100);
				}
			}

			CommunicationServer.Instance.Send(_playerData.ToArray());
		}
		catch (Exception e)
		{
			UCHTools.Log("ERROR: " + e.Message + e.StackTrace);
		}
		finally
		{
			_testScenarios = null;
			_playerData = null;
		}
	}

	private async Task StartCoroutineAsync(IEnumerator coroutine)
	{
		await Task.Run(async () =>
		{
			bool done = false;

			bool MoveNext()
			{
				try
				{
					return coroutine.MoveNext();
				}
				catch
				{
					done = true;
					throw;
				}
			}

			IEnumerator Iterate()
			{
				while (MoveNext())
					yield return coroutine.Current;

				done = true;
			}

			StartCoroutine(Iterate());

			while (!done)
				await Task.Delay(10);
		});
	}

	private IEnumerator RunScenario(TestScenario testScenario)
	{
		UCHTools.Log("StartOffset: " + testScenario.StartOffset);
		_character.transform.position = _startPosition + testScenario.StartOffset.ToVector3();
		_character.GetComponent<Rigidbody2D>().velocity = Vector2.zero;

		int timeStep = 0;

		Vector2 offsets = Vector2.zero;

		foreach (TestStep testStep in testScenario.Steps)
		{
			if (testStep.PositionOffset.HasValue)
			{
				_character.transform.position += testStep.PositionOffset.Value.ToVector3();
				offsets += testStep.PositionOffset.Value;
			}

			SetActions(testStep);

			for (int i = 0; i < testStep.RepeatCount; i++)
			{
				PlayerData playerData = GetPlayerData(testScenario, _character, timeStep++, testStep.Actions, -offsets);
				_playerData.Add(playerData);
				yield return new WaitForFixedUpdate();
			}
		}

		_playerData.Add(GetPlayerData(testScenario, _character, timeStep, Array.Empty<InputKey>(), -offsets));
	}

	private void SetActions(TestStep testStep)
	{
		foreach (InputKey action in testStep.Actions)
		{
			if (_pressedKeys.Add(action))
				UCHTools.SendKey(action, true);
		}

		foreach (InputKey action in _pressedKeys.ToArray())
		{
			if (testStep.Actions.Contains(action))
				continue;
			UCHTools.SendKey(action, false);
			_pressedKeys.Remove(action);
		}
	}

	private void ClearActions()
	{
		foreach (InputKey action in _pressedKeys.ToArray())
		{
			UCHTools.SendKey(action, false);
			_pressedKeys.Remove(action);
		}
	}

	private static PlayerData GetPlayerData(TestScenario testScenario, Character character, int timeStep, InputKey[] actions, Vector2 offset)
	{
		PlayerData playerData = PlayerData.GetPlayerData(CreateScenarioName(testScenario), character, timeStep, actions);
		playerData.PositionX += offset.x;
		playerData.PositionY += offset.y;
		return playerData;
	}

	private static string CreateScenarioName(TestScenario testScenario)
	{
		return string.Join("_", testScenario.Steps.Select(s => $"[{string.Join(",", s.Actions)}]({s.RepeatCount ?? 0:000})"));
	}
}