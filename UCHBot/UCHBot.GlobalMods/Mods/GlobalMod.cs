using BepInEx;
using GameEvent;
using HarmonyLib;
using UCHBot.Comms.Requests;
using UCHBot.GlobalMods.Events;
using UCHBot.GlobalMods.Tools;
using UCHBot.Model;
using UCHBot.Model.GameModels;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace UCHBot.GlobalMods.Mods;

[BepInPlugin(nameof(GlobalMod), nameof(GlobalMod), "1.0.0")]
[BepInDependency(nameof(CommunicationServer))]
public class GlobalMod : BaseUnityPlugin, IGameEventListener
{
	private void Awake()
	{
		new Harmony("patch.uch.xxxprod.com").PatchAll();

		GameEventManager.ChangeListener<StartPhaseEvent>(this, true);
		GameEventManager.ChangeListener<LevelResetEvent>(this, true);
		GameEventManager.ChangeListener<EndPhaseEvent>(this, true);
		GameEventManager.ChangeListener<GameStartEvent>(this, true);
		GameEventManager.ChangeListener<RoundCompleteEvent>(this, true);
		GameEventManager.ChangeListener<PlayersDoneRunning>(this, true);
		GameEventManager.ChangeListener<PlayerTouchedGoalEvent>(this, true);
		GameEventManager.ChangeListener<PlayerKilledEvent>(this, true);
		GameEventManager.ChangeListener<LevelLoadedEvent>(this, true);
		GameEventManager.ChangeListener<LevelDestroyedEvent>(this, true);

		SceneManager.sceneLoaded += OnSceneLoaded;

		CommunicationServer.Instance.RegisterMessageHandler<ServerPingRequest>(ServerPingRequest.RequestKey, _ =>
		{
			CommunicationServer.Instance.Send(new ServerPingRequest());
		});
		CommunicationServer.Instance.RegisterMessageHandler<ShutdownRequest>("quit", _ =>
		{
			Application.Quit();
		});
		
		Logger.LogInfo($"Plugin {nameof(GlobalMod)} is loaded!");
	}

	private void OnSceneLoaded(Scene arg0, LoadSceneMode arg1)
	{
		if (arg0.name is "MainMenu" or "TreeHouseLobby")
			GameEventManager.SendEvent(new LevelDestroyedEvent());
	}


	public void handleEvent(GameEvent.GameEvent e)
	{
		switch (e)
		{
			case EndPhaseEvent { Phase: GameControl.GamePhase.START or GameControl.GamePhase.PLACE } spe:
				UCHTools.Log($"EndPhaseEvent: {spe.Phase}");
				LevelModel levelModel = LobbyManager.instance.CurrentGameController.GetLevelModel();

				GameEventManager.SendEvent(new LevelLoadedEvent(levelModel));
				break;


			default:
				UCHTools.Log(e.GetType().Name);
				break;
		}
	}
}