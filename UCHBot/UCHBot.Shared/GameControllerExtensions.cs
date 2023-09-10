using System.Xml;
using UCHBot.Model;
using UCHBot.Model.Utils;

namespace UCHBot.Shared;

public static class GameControllerExtensions
{
	public static PlayerModel GetPlayerModel(this Character character)
	{
		return new PlayerModel(new Vector2(
			character.transform.position.x,
			character.transform.position.y)
		);
	}

	public static LevelModel GetLevelModel(this GameControl gameController)
	{
		QuickSaver quickSaver = gameController.GetComponent<QuickSaver>();
		XmlDocument xml = quickSaver.GetCurrentXmlSnapshot(true);

		return LevelModel.LoadFromXml(xml);
	}
}