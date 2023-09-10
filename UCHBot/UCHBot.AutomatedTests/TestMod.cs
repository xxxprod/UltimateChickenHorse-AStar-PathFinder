using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using BepInEx;
using UCHBot.GlobalMods;
using UCHBot.GlobalMods.Communications;
using UCHBot.GlobalMods.Mods;
using UCHBot.Shared;
using UCHBot.Shared.Modules;
using UCHBot.Shared.Recording;
using UCHBot.TestMod;
using UnityEngine;
using static GameState;
using static InputEvent;

namespace UCHBot.AutomatedTests;

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
		Logger.LogInfo($"Plugin {PluginInfo.PLUGIN_GUID} is loaded!");

		CommunicationServer.Instance.RegisterMessageHandler<TestScenario[]>("runTest", RunTest);
		CommunicationServer.Instance.RegisterMessageHandler<PlayerData[]>("testFinished", null);
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

		StartCoroutine(RunTestScenarios());
	}

	private IEnumerator RunTestScenarios()
	{
		return InitializeTestSetup()
			.Concat(RunScenario())
			.GetEnumerator();
	}

	private static IEnumerable<object> InitializeTestSetup()
	{
		UCHTools.Log("TestSetup Initializing.");

		yield return new WaitForSeconds(1);
		TreeHouseLoaderModule.LoadTreeHouse(GameMode.FREEPLAY);
		while (!CharacterSelectorModule.SelectCharacter(Character.Animals.RACCOON))
			yield return new WaitForSeconds(1);

		UCHTools.Log("TestSetup Initialized.");
	}

	private IEnumerable<object> RunScenario()
	{
		bool returnToTreeHouse = false;
		foreach (IGrouping<string, TestScenario> testScenariosByLevel in _testScenarios.GroupBy(a => a.LevelName))
		{
			yield return new WaitForSeconds(1);

			if (returnToTreeHouse)
			{
				LobbyManager.instance.ServerChangeScene("TreeHouseLobby");
				yield return new WaitForSeconds(1);
			}

			returnToTreeHouse = true;

			LevelLoaderModule.LoadSavedLevel(testScenariosByLevel.Key, PortalID.CUSTOMA);
			yield return new WaitForSeconds(1);

			StartLevelModule.StartLevelOnPortal(PortalID.CUSTOMA);

			yield return new WaitForSeconds(1);
			UCHTools.SendKey(InputKey.Back, true);
			yield return new WaitForSeconds(1);
			UCHTools.SendKey(InputKey.Back, false);

			_character = UCHTools.GetCharacter();
			_startPosition = _character.transform.position;


			foreach (TestScenario testScenario in testScenariosByLevel)
			{
				Debug.Log($"Starting Scenario {CreateScenarioName(testScenario)}");


				foreach (object p in RunScenario(testScenario)) yield return p;

				ClearActions();

				yield return new WaitForFixedUpdate();
			}
		}

		CommunicationServer.Instance.Send(_playerData.ToArray());
	}

	private IEnumerable RunScenario(TestScenario testScenario)
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