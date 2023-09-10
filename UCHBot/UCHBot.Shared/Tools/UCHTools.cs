using Newtonsoft.Json;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using Newtonsoft.Json.Converters;
using UnityEngine;

namespace UCHBot.Shared;

public static class UCHTools
{
	public static IEnumerable<Character> GetCharacters()
	{
		if (LobbyManager.instance == null)
			yield break;

		if (LobbyManager.instance.CurrentGameController != null)
		{
			foreach (GamePlayer player in LobbyManager.instance.CurrentGameController.CurrentPlayerQueue)
			{
				yield return player.CharacterInstance;
			}
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

	public static void OverrideInputKey(InputEvent.InputKey key, bool pressed)
	{
		KeyboardInput keyboard = GetKeyboard();

		KeyCode? key1 = keyboard.GetKeyBinding(key);

		InputWrapper.SetKeyPressed(key1!.Value, pressed);
	}

	public static void OverrideInputKeys(string[] pressedKeys)
	{
		InputWrapper.Clear();
		foreach (string pressedKey in pressedKeys)
		{
			OverrideInputKey((InputEvent.InputKey)Enum.Parse(typeof(InputEvent.InputKey), pressedKey), true);
		}
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

		Process.Start(new ProcessStartInfo(executable, "-screen-width 1024 -screen-height 768"));
	}
}