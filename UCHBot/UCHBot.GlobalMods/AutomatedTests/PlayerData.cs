using Newtonsoft.Json;
using UCHBot.GlobalMods.Tools;
using UnityEngine;

namespace UCHBot.GlobalMods.Model;

public class PlayerData : Dictionary<string, object>
{
	public string[] Actions => (string[])this["Actions"];

	[JsonIgnore]
	public float PositionX
	{
		get => (float)this["PositionX"];
		set => this["PositionX"] = value;
	}

	[JsonIgnore]
	public float PositionY
	{
		get => (float)this["PositionY"];
		set => this["PositionY"] = value;
	}

	public static PlayerData GetPlayerData(string scenarioName, Character character, int timeStep, IList<InputEvent.InputKey> inputKeys = null)
	{
		Vector2 velocity = character.GetComponent<Rigidbody2D>().velocity;
		Vector3 position = character.transform.position;

		if (inputKeys == null)
		{
			inputKeys = new List<InputEvent.InputKey>();

			if (UCHTools.GetKey(InputEvent.InputKey.Jump)) inputKeys.Add(InputEvent.InputKey.Jump);
			if (UCHTools.GetKey(InputEvent.InputKey.Sprint)) inputKeys.Add(InputEvent.InputKey.Sprint);
			if (UCHTools.GetKey(InputEvent.InputKey.Up)) inputKeys.Add(InputEvent.InputKey.Up);
			if (UCHTools.GetKey(InputEvent.InputKey.Down)) inputKeys.Add(InputEvent.InputKey.Down);
			if (UCHTools.GetKey(InputEvent.InputKey.Left)) inputKeys.Add(InputEvent.InputKey.Left);
			if (UCHTools.GetKey(InputEvent.InputKey.Right)) inputKeys.Add(InputEvent.InputKey.Right);
			if (UCHTools.GetKey(InputEvent.InputKey.Inventory)) inputKeys.Add(InputEvent.InputKey.Inventory);
		}

		PlayerData data = new()
		{
			["ScenarioName"] = scenarioName,
			["TimeStep"] = timeStep,
			["Actions"] = inputKeys.Select(a => a.ToString()).ToArray(),
			["PositionX"] = position.x,
			["PositionY"] = position.y,
			["VelocityX"] = velocity.x,
			["VelocityY"] = velocity.y,
			["OnGround"] = character.GetField<bool>("onGround"),
			["OnWall"] = character.GetField<bool>("onWall"),
			["CanJump"] = character.GetField<bool>("canJump"),
			["Jumping"] = character.GetField<bool>("jumping"),
			["LookingUp"] = character.GetField<bool>("lookingUp"),
			["CrouchingDown"] = character.GetField<bool>("crouchingDown"),
			["LeftColliding"] = character.Left.Colliding | character.Left.CollidingWall | character.Left.CollidingHazard,
			["RightColliding"] = character.Right.Colliding | character.Right.CollidingWall | character.Right.CollidingHazard,
			["HeadColliding"] = character.Head.Colliding | character.Head.CollidingWall | character.Head.CollidingHazard,
			["FeetColliding"] = character.Feet.Colliding | character.Feet.CollidingWall | character.Feet.CollidingHazard
		};

		return data;
	}
}