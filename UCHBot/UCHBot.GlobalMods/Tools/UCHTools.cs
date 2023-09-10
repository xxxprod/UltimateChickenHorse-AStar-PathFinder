using System.Diagnostics;
using System.IO;
using System.Runtime.CompilerServices;
using System.Threading;
using System.Threading.Tasks;
using System.Xml;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using UCHBot.Model.GameModels;
using UnityEngine;
using static GameState;
using UnityEngine.SceneManagement;
using static InputEvent;
using Formatting = Newtonsoft.Json.Formatting;

namespace UCHBot.GlobalMods.Tools;

public static class UCHTools
{
	private static string _previouslyLaunchedLevel;

	public static IEnumerable<Character> GetCharacters()
	{
		if (LobbyManager.instance == null)
			yield break;

		if (LobbyManager.instance.CurrentGameController != null)
		{
			foreach (GamePlayer player in LobbyManager.instance.CurrentGameController.CurrentPlayerQueue)
				yield return player.CharacterInstance;
		}
		else
		{
			foreach (LobbyPlayer player in LobbyManager.instance.GetLobbyPlayers())
			{
				yield return player.CharacterInstance;
			}
		}
	}

	public static KeyboardInput GetKeyboard()
	{
		GameState gameState = GameState.GetInstance();
		KeyboardInput keyboard = gameState?.Keyboard;
		return keyboard;
	}

	public static Character GetCharacter()
	{
		LobbyPlayer lobbyPlayer = LobbyManager.instance.GetLobbyPlayers().First();
		Character character = lobbyPlayer.LocalPlayer.PlayerCharacter;
		return character;
	}

	public static bool GetKey(InputEvent.InputKey key)
	{
		KeyboardInput keyboard = GetKeyboard();

		KeyCode? key1 = keyboard.GetKeyBinding(key);
		KeyCode? key2 = keyboard.GetAltKeyBinding(key);

		Dictionary<int, bool> lastKeyState = keyboard.GetField<Dictionary<int, bool>>("lastKeyState");

		return (key1 != null && lastKeyState[(int)key1.Value]) || (key2 != null && lastKeyState[(int)key2.Value]);
	}

	public static void OverrideInputKey(string key, bool pressed)
	{
		OverrideInputKey((InputKey)Enum.Parse(typeof(InputKey), key), pressed);
	}

	public static void OverrideInputKey(InputKey key, bool pressed)
	{
		KeyboardInput keyboard = GetKeyboard();

		KeyCode? key1 = keyboard.GetKeyBinding(key);

		InputWrapper.SetKeyPressed(key1!.Value, pressed);
	}

	public static void OverrideInputKeys(string[] pressedKeys)
	{
		InputWrapper.Clear();
		foreach (string pressedKey in pressedKeys)
			OverrideInputKey(pressedKey, true);
	}

	public static void OverrideInputKeys(InputKey[] pressedKeys)
	{
		InputWrapper.Clear();
		foreach (InputKey pressedKey in pressedKeys)
			OverrideInputKey(pressedKey, true);
	}

	public static void OverrideInputKeys(PlayerAction[] pressedKeys)
	{
		InputWrapper.Clear();
		foreach (PlayerAction pressedKey in pressedKeys)
			OverrideInputKey(pressedKey.ToString(), true);
	}

	public static void SendKey(InputEvent.InputKey key, bool pressed)
	{
		KeyboardInput keyboard = GetKeyboard();
		SendKey(keyboard, key, pressed);
	}

	public static void SendKey(this Controller keyboard, InputEvent.InputKey key, bool pressed)
	{
		keyboard.Notify(new InputEvent(1, key, pressed, true));
	}

	public static void Log(object message = null, [CallerMemberName] string callerMember = null, [CallerFilePath] string callerFile = null)
	{
		string fileName = Path.GetFileNameWithoutExtension(callerFile);

		JsonConvert.DefaultSettings = () => new JsonSerializerSettings
		{
			Formatting = Formatting.None,
			Converters =
			{
				new StringEnumConverter()
			}
		};

		UnityEngine.Debug.Log(message == null
			? $"({Time.time}) [{fileName}].{callerMember} called"
			: $"({Time.time}) [{fileName}].{callerMember}: {JsonConvert.SerializeObject(message)}");
	}

	public static void CopyModsAndStartGame()
	{
		string gameDirectory = Path.GetFullPath("..\\..\\..\\..\\..\\UltimateChickenHorse");
		string modDirectory = Path.Combine(gameDirectory, "BepInEx", "plugins", "UCHBot");
		string executable = Path.Combine(gameDirectory, "UltimateChickenHorse.exe");

		if (Directory.Exists(modDirectory))
			Directory.Delete(modDirectory, true);

		Thread.Sleep(500);

		Directory.CreateDirectory(modDirectory);

		Directory.GetFiles(".", "UCHBot*.dll").ToList()
			.ForEach(file => File.Copy(file, Path.Combine(modDirectory, Path.GetFileName(file))));

		Process.Start(new ProcessStartInfo(executable, "-screen-width 1920 -screen-height 1080"));
		//Process.Start(new ProcessStartInfo(executable, "-screen-width 1024 -screen-height 768"));
	}

	public static void Message(string message)
	{
		UserMessageManager.Instance.UserMessage(message);
		Log(message);
	}

	public static async Task LaunchLevel(string levelName, GameMode gameMode)
	{
		try
		{
			if (_previouslyLaunchedLevel == levelName)
			{
				Log($"Level {levelName} was already loaded, reusing it.");
				return;
			}

			Log($"Loaded Level has changed from {_previouslyLaunchedLevel} to {levelName}. Going back to TreeHouse.");
			_previouslyLaunchedLevel = levelName;
			//if(controller == null || controller.GetLevelModel().Name != levelName)

			if (SceneManager.GetActiveScene().name != "MainMenu")
			{
				Log($"Going back to MainMenu");
				LobbyManager.instance?.CurrentGameController.BackToMainMenu();

				while (SceneManager.GetActiveScene().name != "MainMenu")
					await Task.Delay(100);
			}

			GameState gameState = GameState.GetInstance();
			KeyboardInput keyboard = gameState.Keyboard;

			Log("Start loading tree house scene");

			GameObject mainMenuControl = GameObject.Find(nameof(MainMenuControl));
			MainMenuControl menuControl = mainMenuControl.GetComponent<MainMenuControl>();
			menuControl.JoinControllerToMainMenu(keyboard, true);

			// ReSharper disable once MethodHasAsyncOverload
			SceneManagerWrapper.LoadScene("TreeHouseLobby");

			GameSettings gameSettings = GameSettings.GetInstance();
			gameSettings.GameMode = gameMode;

			while (!SelectCharacter(Character.Animals.RACCOON))
				await Task.Delay(2000);


			CustomLevelPortal portal = LoadSavedLevel(levelName, PortalID.CUSTOMA);

			await Task.Delay(2000);

			LobbyManager.instance?.CurrentLevelSelectController.LaunchLevel(portal);
			await Task.Delay(3000);
		}
		catch (Exception e)
		{
			Log($"Exception: {e.Message + e.StackTrace}");
		}
	}
	
	private static CustomLevelPortal LoadSavedLevel(string levelName, GameState.PortalID targetPortal)
	{
		Log($"Start loading level {levelName} into portal {targetPortal}");

		XmlDocument levelDocument = QuickSaver.TryLoadSnapshotXMLFromPath($"{QuickSaver.LocalSavesFolder}/{levelName}.c.snapshot");

		CustomLevelPortal portal = (CustomLevelPortal)LobbyManager.instance.CurrentLevelSelectController.portals.First(a => a.PortalID == targetPortal);

		CustomLevelPortal.AuthorInfo authorInfo = new("123", "PluginLevelLoader", "",
			LobbyPlayer.SocialPlatform.Undefined);

		portal.ClearContents();
		portal.SetContents(LevelName.BLANKLEVEL, levelName, levelName, levelDocument.OuterXml,
			portal.levelImage.sprite, authorInfo);
		

		GetInstance().currentSnapshotInfo.snapshotName = levelName;

		Log($"Finished loading level {levelName} into portal {targetPortal}");

		return portal;
	}

	private static bool SelectCharacter(Character.Animals animal)
	{
		if (LobbyManager.instance?.GetLobbyPlayers()?.FirstOrDefault() == null)
			return false;

		Log($"Start selecting animal {animal}");

		LobbyPlayer lobbyPlayer = LobbyManager.instance.GetLobbyPlayers().First();

		Character character = Character.AllCharacters.First(a => a.CharacterSprite == animal);

		lobbyPlayer.RequestPickCharacter(character);

		Log($"Finished selecting animal {animal}");

		return true;
	}
}