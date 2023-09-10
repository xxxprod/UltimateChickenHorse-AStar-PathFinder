using UnityEngine;

namespace UCHBot.GlobalMods.AutomatedTests;

public class TestStep
{
    public InputEvent.InputKey[] Actions { get; set; } = Array.Empty<InputEvent.InputKey>();
    public int? RepeatCount { get; set; }
    public int[] RepeatCounts { get; set; }
    public Vector2? PositionOffset { get; set; }
}