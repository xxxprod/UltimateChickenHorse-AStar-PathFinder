using BepInEx;
using GameEvent;
using UCHBot.Comms.Requests;
using UCHBot.GlobalMods.Events;
using UnityEngine;

namespace UCHBot.GlobalMods.Mods;

[BepInPlugin(nameof(PathRendererMod), nameof(PathRendererMod), "1.0.0")]
[BepInDependency(nameof(PathFinderMod))]
public class PathRendererMod : BaseUnityPlugin, IGameEventListener
{
	private LineRenderer[] _lines;

	private void Awake()
	{
		GameEventManager.ChangeListener<LevelDestroyedEvent>(this, true);

		CommunicationServer.Instance.RegisterMessageHandler<ExecuteGeneratedPathRequest>(ExecuteGeneratedPathRequest.RequestKey, ShowPaths);
		CommunicationServer.Instance.RegisterMessageHandler<ShowPathRequest>(ShowPathRequest.RequestKey, ShowPaths);

		_lines = Enumerable.Range(0, 10).Select(i =>
		{
			GameObject obj = new()
			{
				transform =
				{
					parent = transform
				}
			};
			LineRenderer lineRenderer = obj.AddComponent<LineRenderer>();
			lineRenderer.startWidth = 0.1f;
			lineRenderer.endWidth = 0.1f;
			lineRenderer.useWorldSpace = true;
			lineRenderer.material = new Material(Shader.Find("Sprites/Default"))
			{
				color = (i % 4) switch
				{
					0 => Color.red,
					1 => Color.green,
					2 => Color.blue,
					3 => Color.yellow,
					_ => Color.white
				}
			};
			lineRenderer.sortingLayerName = "Player";

			lineRenderer.sortingOrder = i % 2 == 0 ? 100 : -100;

			return lineRenderer;
		}).ToArray();

		Logger.LogInfo($"Plugin {nameof(PathRendererMod)} is loaded!");
	}

	private void ShowPaths(PathRequestBase obj)
	{
		ResetPaths();

		for (int i = 0; i < _lines.Length && i < obj.Paths.Length; i++)
		{
			_lines[i].positionCount = obj.Paths[i].Nodes.Count;
			_lines[i].SetPositions(obj.Paths[i].Nodes.Select(n => new Vector3(n.Position.X, n.Position.Y)).ToArray());
		}
	}

	public void handleEvent(GameEvent.GameEvent e)
	{
		switch (e)
		{
			case LevelDestroyedEvent:
				ResetPaths();
				break;
		}
	}

	private void ResetPaths()
	{
		foreach (LineRenderer line in _lines)
			line.positionCount = 0;
	}
}