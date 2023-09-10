using System.Threading.Tasks;
using BepInEx;
using UCHBot.Comms.Requests;
using UCHBot.GlobalMods.Tools;
using static GameState;

namespace UCHBot.GlobalMods.Mods;

[BepInPlugin(nameof(GeneratePathFinderRequestMod), nameof(GeneratePathFinderRequestMod), "1.0.0")]
[BepInDependency(nameof(GlobalMod))]
public class GeneratePathFinderRequestMod : BaseUnityPlugin
{
	private void Awake()
	{
		CommunicationServer.Instance.RegisterMessageHandler<GeneratePathRequest>(GeneratePathRequest.RequestKey, null);
		CommunicationServer.Instance.RegisterMessageHandler<CreatePathGeneratorRequest>(CreatePathGeneratorRequest.RequestKey, request =>
		{
			_ = LoadLevelAndSendRequest(request.LevelCode);
		});


		Logger.LogInfo($"Plugin {nameof(TestMod)} is loaded!");
	}

	private async Task LoadLevelAndSendRequest(string levelName)
	{
		await UCHTools.LaunchLevel(levelName, GameMode.CHALLENGE);

		await Task.Delay(2000);

		UCHTools.Log($"Sending GeneratePathRequest");

		CommunicationServer.Instance.Send(new GeneratePathRequest(
			LobbyManager.instance.CurrentGameController.GetLevelModel(),
			UCHTools.GetCharacters().Single().GetPlayerModel()
		));
	}
}