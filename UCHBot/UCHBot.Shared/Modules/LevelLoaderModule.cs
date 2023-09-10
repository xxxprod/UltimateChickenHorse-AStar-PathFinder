using System.Xml;

namespace UCHBot.Shared.Modules;

public static class LevelLoaderModule
{
	public static void LoadSavedLevel(string levelName, GameState.PortalID targetPortal)
    {
        UCHTools.Log($"Start loading level {levelName} into portal {targetPortal}");

        XmlDocument levelDocument = QuickSaver.TryLoadSnapshotXMLFromPath($"{QuickSaver.LocalSavesFolder}/{levelName}.c.snapshot");

        CustomLevelPortal portal = (CustomLevelPortal)LobbyManager.instance.CurrentLevelSelectController.portals.First(a => a.PortalID == targetPortal);

        CustomLevelPortal.AuthorInfo authorInfo = new("123", "PluginLevelLoader", "",
            LobbyPlayer.SocialPlatform.Undefined);

        portal.SetContents(GameState.LevelName.BLANKLEVEL, levelName, "xxxx", levelDocument.OuterXml,
            portal.levelImage.sprite, authorInfo);

        UCHTools.Log($"Finished loading level {levelName} into portal {targetPortal}");
    }
}