using BepInEx;
using BepInEx.Configuration;
using GameEvent;
using UCHBot.GlobalMods.Events;
using UCHBot.GlobalMods.Tools;
using UCHBot.Model.GameModels;
using UnityEngine;

namespace UCHBot.GlobalMods.Mods;

[BepInPlugin(nameof(LevelModelVisualizerMod), nameof(LevelModelVisualizerMod), "1.0.0")]
public class LevelModelVisualizerMod : BaseUnityPlugin, IGameEventListener
{
	private GameObject[] _rectangleBlocks;
	private GameObject _playerOutline;
	private GameObject _playerDeath;
	private ConfigEntry<bool> _enabled;

	private void Awake()
	{
		_enabled = Config.Bind("Visualizer", "Enabled", false, "Enables/Disables the Level Block Visualizer");

		GameEventManager.ChangeListener<LevelLoadedEvent>(this, true);
		GameEventManager.ChangeListener<LevelDestroyedEvent>(this, true);
		GameEventManager.ChangeListener<LevelResetEvent>(this, true);
		GameEventManager.ChangeListener<PlayerKilledEvent>(this, true);
		GameEventManager.ChangeListener<StartPhaseEvent>(this, true);

		Logger.LogInfo($"Plugin {nameof(LevelModelVisualizerMod)} is loaded!");
	}

	public void handleEvent(GameEvent.GameEvent e)
	{
		switch (e)
		{
			// 1
			case LevelLoadedEvent gse:
				if(!_enabled.Value)
					return;
				DestroyRectangles();
				LevelModel level = gse.LevelModel;
				_rectangleBlocks = level.Blocks
					.Select(block =>
					{
						return VisualTools.CreateRectangle(
							x: block.Bounds.Left,
							y: block.Bounds.Bottom,
							width: block.Bounds.Size.X,
							height: block.Bounds.Size.Y,
							color: block.CollisionType switch
							{
								CollisionType.Block => Color.blue,
								CollisionType.Goal => Color.green,
								CollisionType.Death => Color.red,
								CollisionType.DeathPit => new Color(0.5f, 0, 0),
								var b when (b & CollisionType.LevelBorder) > 0 => Color.white,
								_ => throw new ArgumentOutOfRangeException()
							},
							onTop: false);
					})
					.ToArray();
				break;

			case LevelResetEvent:
				if(!_enabled.Value)
					return;
				//case StartPhaseEvent spe:
				//	if (spe.Phase == GameControl.GamePhase.WAIT)
				{
					DestroyPlayerOutline();
					DestroyPlayerDeath();

					//List<Placeable> placeables = FindObjectsOfType<Placeable>().ToList();

					//foreach (Placeable placeable in placeables)
					//{
					//	PrintCollider(placeable);
					//}


					//Character character = UCHTools.GetCharacters().Single();
					//PrintCollider(character);


					PlayerModel player = UCHTools.GetCharacters().Single().GetPlayerModel();
					UCHTools.Log($"Drawing Player Outline at: {player.Bounds}");
					_playerOutline = VisualTools.CreateRectangle(
						x: player.Bounds.Left,
						y: player.Bounds.Bottom,
						width: player.Bounds.Size.X,
						height: player.Bounds.Size.Y,
						color: new Color(0.5f, 0.5f, 1f, 0.8f),
						onTop: true);
				}
				break;
			case PlayerKilledEvent:
				if(!_enabled.Value)
					return;
				{
					DestroyPlayerDeath();

					Character character = UCHTools.GetCharacters().Single();
					PlayerModel player = character.GetPlayerModel();
					UCHTools.Log($"Drawing Player Death at: {player.Bounds}");
					_playerDeath = VisualTools.CreateRectangle(
						x: player.Bounds.Left,
						y: player.Bounds.Bottom,
						width: player.Bounds.Size.X,
						height: player.Bounds.Size.Y,
						color: Color.yellow,
						onTop: false);
				}

				break;

			// 3
			case LevelDestroyedEvent:
				DestroyRectangles();
				DestroyPlayerOutline();
				DestroyPlayerDeath();
				break;
		}
	}

	private static void PrintCollider(MonoBehaviour obj)
	{
		if (obj.gameObject.name is "DeathPit" or "Ceiling" or "LeftWall" or "RightWall")
			return;

		UCHTools.Log();
		UCHTools.Log($"{obj.GetType().Name}, {obj.gameObject.name}: pos: {obj.transform.position}, scale: {obj.transform.localScale}");
		Collider2D[] collider2Ds = obj.GetComponentsInChildren<Collider2D>();
		foreach (Collider2D collider2D in collider2Ds)
		{
			if (collider2D.name is "PlacementCollider" or "InnerHazard" or "GoalAreaPlacementCollider" or "CoinGrabber")
				continue;
			switch (collider2D)
			{
				case BoxCollider2D boxCollider2D:
					UCHTools.Log($"BoxCollider: {collider2D.name}, " +
								 $"'offset': {boxCollider2D.offset}, " +
								 $"'size': {boxCollider2D.size}, " +
								 $"'scale': {collider2D.gameObject.transform.localScale}, " +
								 $"localPos: {collider2D.gameObject.transform.localPosition}, " +
								 $"friction: {collider2D.friction}");
					break;
				case CircleCollider2D circleCollider2D:
					UCHTools.Log($"CircleCollider: {collider2D.name}, " +
								 $"'offset': {collider2D.offset}, " +
								 $"'radius': {circleCollider2D.radius}, " +
								 $"'scale': {collider2D.gameObject.transform.localScale}, " +
								 $"localPos: {collider2D.gameObject.transform.localPosition}" +
								 $"friction: {collider2D.friction}");
					break;
				case CapsuleCollider2D capsuleCollider2D:
					UCHTools.Log($"CapsuleCollider: {collider2D.name}, " +
								 $"'offset': {collider2D.offset}, " +
								 $"'size': {capsuleCollider2D.size}, " +
								 $"'scale': {collider2D.gameObject.transform.localScale}, " +
								 $"localPos: {collider2D.gameObject.transform.localPosition}" +
								 $"friction: {collider2D.friction}");
					break;
				default:
					UCHTools.Log($"Unknown Collider: {collider2D.name}, {collider2D}");
					break;
			}
		}
	}

	private void Update()
	{
		if (_playerOutline != null)
		{
			PlayerModel player = UCHTools.GetCharacters().Single().GetPlayerModel();
			_playerOutline.transform.position = new Vector3(player.Bounds.Left, player.Bounds.Bottom, 0);
		}
	}

	private void DestroyRectangles()
	{
		if (_rectangleBlocks != null)
		{
			foreach (GameObject rectangleBlock in _rectangleBlocks)
			{
				Destroy(rectangleBlock);
			}

			_rectangleBlocks = null;
		}
	}

	private void DestroyPlayerOutline()
	{
		if (_playerOutline != null)
		{
			Destroy(_playerOutline);
			_playerOutline = null;
		}
	}

	private void DestroyPlayerDeath()
	{
		if (_playerDeath != null)
		{
			Destroy(_playerDeath);
			_playerDeath = null;
		}
	}
}