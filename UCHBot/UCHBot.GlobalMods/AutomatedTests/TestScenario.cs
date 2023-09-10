using UnityEngine;

namespace UCHBot.GlobalMods.AutomatedTests;

public class TestScenario
{
	public string LevelName { get; set; }
	public Vector2 StartOffset { get; set; }
	public TestStep[] Steps { get; set; }
}