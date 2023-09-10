namespace UCHBot.Shared.Modules;

public static class StartLevelModule
{
    public static bool StartLevelOnPortal(GameState.PortalID targetPortal)
    {
        UCHTools.Log($"Start level on portal {targetPortal}");

        LobbyPlayer lobbyPlayer = LobbyManager.instance.GetLobbyPlayers().First();

        LevelPortal portal = LobbyManager.instance.CurrentLevelSelectController.portals
            .First(a => a.PortalID == targetPortal);

        lobbyPlayer.CharacterInstance.transform.position = portal.transform.position;

        LobbyManager.instance.CurrentLevelSelectController.LaunchLevel(portal);

        UCHTools.Log($"Level on portal {targetPortal} started");
        
        return true;
    }
}