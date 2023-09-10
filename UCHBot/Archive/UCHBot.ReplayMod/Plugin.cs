using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using BepInEx;
using GameEvent;
using UCHBot.GlobalMods.Events;
using UCHBot.GlobalMods.Model;
using UCHBot.GlobalMods.Tools;
using UnityEngine;

namespace UCHBot.ReplayMod;

[BepInPlugin(PluginInfo.PLUGIN_GUID, PluginInfo.PLUGIN_NAME, PluginInfo.PLUGIN_VERSION)]
public class Plugin : BaseUnityPlugin, IGameEventListener
{
    private int _timeStep;
    private PlayerData[] _playerData = Array.Empty<PlayerData>();
    private bool _replay;
    private LineRenderer[] _lines;
    private Character _replayChar;
    private PathResultData _playerDatas;

    private void Awake()
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

        
        _playerDatas = TestResultsLogger.LoadData<PathResultData>("JumpPointsActions.json");
        StartCoroutine(LoadLevel());

        _lines = Enumerable.Range(0, 200).Select(a =>
        {
            var obj = new GameObject
            {
                transform =
                {
                    parent = transform
                }
            };
            LineRenderer lineRenderer = obj.AddComponent<LineRenderer>();
            lineRenderer.material = new Material(Shader.Find("Sprites/Default"));
            return lineRenderer;
        }).ToArray();
    }

    private IEnumerator LoadLevel()
    {
        yield return new WaitForSeconds(1);
        TreeHouseLoaderModule.LoadTreeHouse(GameState.GameMode.CHALLENGE);
        while (!CharacterSelectorModule.SelectCharacter(Character.Animals.RACCOON))
            yield return new WaitForSeconds(1);

        LevelLoaderModule.LoadSavedLevel(_playerDatas.LevelName, GameState.PortalID.CUSTOMA);
        yield return new WaitForSeconds(1);
        StartLevelModule.StartLevelOnPortal(GameState.PortalID.CUSTOMA);
        yield return new WaitForSeconds(1);
    }

    public void handleEvent(GameEvent.GameEvent e)
    {
        UCHTools.Log(e.GetType().Name);

        switch (e)
        {
            case GameEndEvent:
                InputWrapper.Clear();
                _replay = false;
                break;
            case LevelResetEvent:
                if (_replayChar is null)
                {
                    _replayChar = Instantiate(UCHTools.GetCharacter().gameObject).GetComponent<Character>();
                    _replayChar.UpperBodyCollider.enabled = false;
                    _replayChar.LowerBodyCollider.enabled = false;
                    _replayChar.headCollider.enabled = false;
                }

                UCHTools.OverrideInputKey(InputEvent.InputKey.Accept, false);
                UCHTools.OverrideInputKey(InputEvent.InputKey.Down, false);
                UCHTools.OverrideInputKey(InputEvent.InputKey.Up, false);
                UCHTools.OverrideInputKey(InputEvent.InputKey.Jump, false);
                UCHTools.OverrideInputKey(InputEvent.InputKey.Sprint, false);
                UCHTools.OverrideInputKey(InputEvent.InputKey.Left, false);
                UCHTools.OverrideInputKey(InputEvent.InputKey.Right, false);

                int i;
                for (i = 0; i < _playerDatas.Paths.Length; i++)
                {
                    Vector3[] pos = _playerDatas.Paths[i].Select(a => new Vector3(a.PositionX, a.PositionY)).ToArray();
                    _lines[i].startWidth = 0.1f;
                    _lines[i].endWidth = 0.1f;
                    _lines[i].material.color = (i % 4) switch
                    {
                        0 => Color.red,
                        1 => Color.green,
                        2 => Color.blue,
                        3 => Color.yellow,
                        _ => Color.white
                    };
                    _lines[i].positionCount = pos.Length;
                    _lines[i].SetPositions(pos.ToArray());
                    _lines[i].useWorldSpace = true;

                    _lines[i].SetPositions(Array.Empty<Vector3>());
                }

                foreach (Bounds block in _playerDatas.Blocks)
                {
                    Vector3[] pos = {
                        new(block.PositionX, block.PositionY),
                        new(block.PositionX + block.Width, block.PositionY),
                        new(block.PositionX + block.Width, block.PositionY + block.Height),
                        new(block.PositionX, block.PositionY + block.Height),
                        new(block.PositionX, block.PositionY)
                    };
                    _lines[i].startWidth = 0.2f;
                    _lines[i].endWidth = 0.2f;
                    _lines[i].material.color = Color.black;
                    _lines[i].positionCount = pos.Length;
                    _lines[i].SetPositions(pos.ToArray());
                    _lines[i].useWorldSpace = true;

                    i++;
                }

                foreach (Bounds block in _playerDatas.Goals)
                {
                    Vector3[] pos = new Vector3[]
                    {
                        new(block.PositionX, block.PositionY),
                        new(block.PositionX + block.Width, block.PositionY),
                        new(block.PositionX + block.Width, block.PositionY + block.Height),
                        new(block.PositionX, block.PositionY + block.Height),
                        new(block.PositionX, block.PositionY)
                    };
                    _lines[i].startWidth = 0.1f;
                    _lines[i].endWidth = 0.1f;
                    _lines[i].material.color = Color.blue;
                    _lines[i].positionCount = pos.Length;
                    _lines[i].SetPositions(pos.ToArray());
                    _lines[i].useWorldSpace = true;

                    i++;
                }
                
                _playerData = _playerDatas.Paths[0];

                //_line2.SetPositions(_playerData.Select(a => new Vector3(a.PositionX, a.PositionY)).ToArray());

                _timeStep = -60;
                _replay = true;
                UCHTools.Log("Start replay");
                break;
            case PlayerKilledEvent pke:
                InputWrapper.Clear();

                if (pke.Player.PlayerCharacter == UCHTools.GetCharacter())
                {
                    UCHTools.Log("Replay stopped.");
                    _replay = false;
                }
                break;
            case PlayerTouchedGoalEvent epe:
                InputWrapper.Clear();

                if (epe.Character == UCHTools.GetCharacter())
                {
                    UCHTools.Log("Replay stopped.");
                    _replay = false;
                }
                break;
        }
    }

    private void FixedUpdate()
    {
        if (_replay)
        {
            if (_timeStep >= _playerData.Length)
            {
                _replay = false;
                return;
            }

            if (_timeStep < 0)
            {
                _timeStep++;
                return;
            }

            PlayerData playerData = _playerData[_timeStep++];

            _replayChar.transform.position = new Vector3(playerData.PositionX, playerData.PositionY);
            
            //UCHTools.GetCharacter().transform.position = new Vector3(playerData.PositionX, playerData.PositionY);

            
            UCHTools.OverrideInputKeys(playerData.Actions);

            //UCHTools.OverrideInputKey(InputEvent.InputKey.Jump, playerData.JumpPressed);
            //UCHTools.OverrideInputKey(InputEvent.InputKey.Sprint, playerData.SprintPressed);
            //UCHTools.OverrideInputKey(InputEvent.InputKey.Left, playerData.LeftPressed);
            //UCHTools.OverrideInputKey(InputEvent.InputKey.Right, playerData.RightPressed);
            //UCHTools.OverrideInputKey(InputEvent.InputKey.Up, playerData.UpPressed);
            //UCHTools.OverrideInputKey(InputEvent.InputKey.Down, playerData.DownPressed);

            //Thread.Sleep(100);


            //playerData.Apply(UCHTools.GetCharacter());
        }
    }
}

public class Bounds
{
    public float PositionX { get; set; }
    public float PositionY { get; set; }
    public float Width { get; set; }
    public float Height { get; set; }
}

public class PathResultData
{
    public string LevelName { get; set; }
    public PlayerData[][] Paths { get; set; }
    public Bounds[] Blocks { get; set; }
    public Bounds[] Goals { get; set; }
    public Bounds[] Surfaces { get; set; }
}