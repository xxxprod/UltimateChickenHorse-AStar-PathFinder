using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using BepInEx;
using GameEvent;
using UCHBot.GlobalMods.Events;
using UCHBot.GlobalMods.Model;
using UCHBot.GlobalMods.Tools;
using UnityEngine;

namespace UCHBot.RecorderMod;

[BepInPlugin(PluginInfo.PLUGIN_GUID, PluginInfo.PLUGIN_NAME, PluginInfo.PLUGIN_VERSION)]
public class Plugin : BaseUnityPlugin, IGameEventListener
{
    private int _timeStep;
    private readonly List<PlayerData> _playerData = new();
    private bool _record;
    private bool _replay;
    private bool _replay2;
    private bool _saveData;
    private Character _replayChar;

    private async Task Awake()
    {
        Logger.LogInfo($"Plugin {PluginInfo.PLUGIN_GUID} is loaded!");

        GameEventManager.ChangeListener<StartPhaseEvent>(this, true);
        GameEventManager.ChangeListener<LevelResetEvent>(this, true);
        GameEventManager.ChangeListener<EndPhaseEvent>(this, true);
        GameEventManager.ChangeListener<GameStartEvent>(this, true);
        GameEventManager.ChangeListener<RoundCompleteEvent>(this, true);
        GameEventManager.ChangeListener<PlayersDoneRunning>(this, true);
        GameEventManager.ChangeListener<PlayerTouchedGoalEvent>(this, true);
        GameEventManager.ChangeListener<PlayerKilledEvent>(this, true);

        await UCHTools.LaunchLevel("WideJumpTest", GameState.GameMode.CHALLENGE);
    }

    public void handleEvent(GameEvent.GameEvent e)
    {
        UCHTools.Log(e.GetType().Name);

        Character original = UCHTools.GetCharacter();
        switch (e)
        {
            case PlayerKilledEvent:
                _replay = false;
                _replay2 = false;
                _record = false;
                InputWrapper.Clear();
                if (_replayChar != null)
                {
                    Destroy(_replayChar.gameObject);
                    _replayChar = null;
                }
                break;
            case LevelResetEvent:
                
                if (_replayChar != null)
                {
                    Destroy(_replayChar.gameObject);
                    _replayChar = null;
                }

                InputWrapper.Clear();
                
                if (_replay2)
                {
                    _timeStep = 0;
                    _replayChar = Instantiate(original.gameObject).GetComponent<Character>();
                    _replayChar.UpperBodyCollider.enabled = false;
                    _replayChar.LowerBodyCollider.enabled = false;
                    _replayChar.headCollider.enabled = false;
                    _replay2 = false;
                    _replay = true;
                    UCHTools.Log("Start replay");
                }
                else
                {
                    _timeStep = 0;
                    _playerData.Clear();
                    _record = true;
                    UCHTools.Log("Start recording");
                }

                break;
            case PlayerTouchedGoalEvent epe:
                InputWrapper.Clear();

                Character character = original;
                if (epe.Character == character)
                {
                    if (_replay)
                    {
                        UCHTools.Log("Replay stopped");
                        _replay = false;
                    }
                    else
                    {
                        UCHTools.Log("Recording stopped, Saving...");
                        _record = false;
                        _saveData = true;
                    }
                }
                break;
        }
    }

    private void FixedUpdate()
    {
        if (_record)
        {
            Character character = UCHTools.GetCharacter();
            try
            {
                _playerData.Add(PlayerData.GetPlayerData("recording", character, _timeStep++));
            }
            catch (Exception ex)
            {
                UCHTools.Log(ex.Message + ex.StackTrace);
            }
        }
        else if (_saveData)
        {
            TestResultsLogger.LogResults("Game_Recording", _playerData, true);
            _saveData = false;
            _replay2 = true;
            UCHTools.GetCharacter().WantsToRetry = true;
        }
        else if (_replay)
        {
            if (_timeStep < 0)
            {
                _timeStep++;
                return;
            }

            if (_timeStep >= _playerData.Count)
            {
                return;
            }


            if (_timeStep > 0)
            {
                PlayerData prevData = _playerData[_timeStep];
                Vector3 diff = UCHTools.GetCharacter().transform.position - new Vector3(prevData.PositionX, prevData.PositionY);
                UCHTools.Log($"Pos Diff: [{diff.x:0.000}, {diff.y:0.000}]");
            }

            PlayerData playerData = _playerData[_timeStep++];

            _replayChar.transform.position = new Vector3(playerData.PositionX, playerData.PositionY);

            UCHTools.OverrideInputKeys(playerData.Actions);
        }
    }
}