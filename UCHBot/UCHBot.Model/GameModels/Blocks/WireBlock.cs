namespace UCHBot.Model.GameModels.Blocks;

[DebuggerDisplay("Wire: {Bounds}")]
public class WireBlock : StaticBlock
{
	public static readonly Vector2 Size = new(0.9f, 0.5f);
	private static readonly Vector2 Offset = new((1 - Size.X) / 2, 0);
	public static readonly Dictionary<int, Vector2> Offsets = new()
	{
		[0] = new Vector2(Offset.X, -1.0f),
		[90] = new Vector2(1 - Size.Y, -1.0f + Offset.X),
		[180] = new Vector2(Offset.X, -Size.Y),
		[270] = new Vector2(0, -1.0f + Offset.X),
	};

	public WireBlock(int sceneId, int? parentId, int blockId, Vector2 position, Vector2 size)
		: base(sceneId, parentId, blockId, position, size, CollisionType.Death)
	{
	}

	public new static bool TryParse(XmlNode xmlNode, out IBlock block)
	{
		block = null;

		int blockId = GetBlockId(xmlNode);
		if (blockId is not (11 or 12 or 13 or 55))
			return false;

		// skip wire group elements
		if (GetMainId(xmlNode) == null)
			return true;

		int sceneId = GetSceneId(xmlNode);
		int? parentId = GetParentId(xmlNode);

		int rotation = GetRotation(xmlNode);

		Vector2 position = GetPosition(xmlNode);

		Vector2 size = rotation is 0 or 180
			? Size
			: new Vector2(Size.Y, Size.X);

		Vector2 offset = Offsets[rotation];

		block = new WireBlock(sceneId, parentId, blockId, position + offset, size);

		return true;
	}
}

[DebuggerDisplay("Spike: {Bounds}")]
public class SpikeBlock : StaticBlock
{
	public static readonly Vector2 Size = new(0.9f, 0.9f);
	public static readonly Vector2 Offset = new((1 - Size.X) / 2, -1 + (1 - Size.X) / 2);

	public SpikeBlock(int sceneId, int? parentId, int blockId, Vector2 position)
		: base(sceneId, parentId, blockId, position, Size, CollisionType.Death)
	{
	}

	public new static bool TryParse(XmlNode xmlNode, out IBlock block)
	{
		block = null;

		int blockId = GetBlockId(xmlNode);
		if (blockId is not 10)
			return false;

		int sceneId = GetSceneId(xmlNode);
		int? parentId = GetParentId(xmlNode);

		Vector2 position = GetPosition(xmlNode);

		Vector2 offset = Offset;
		block = new SpikeBlock(sceneId, parentId, blockId, position + offset);

		return true;
	}
}

/*
 

"MultipiecePart, BarbedwirePiece: pos: (-15.0, -9.0, 0.0), scale: (1.0, 1.0, 1.0)"
"BoxCollider: RequiredCollider, 'offset': (0.0, 0.0), 'size': (0.3, 0.3), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, -0.8, 0.0)"
"BoxCollider: Collider, 'offset': (0.0, -0.3), 'size': (0.8, 0.4), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: PlacementColliderAtt, 'offset': (0.0, -0.6), 'size': (0.5, 0.2), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"

"MultipieceBlock, 21_PiecedBarbedWirex1(Clone): pos: (-15.0, -9.0, 0.0), scale: (1.0, 1.0, 1.0)"

"Placeable, 11_1x1 Spike Block(Clone): pos: (-4.0, -9.0, 0.0), scale: (1.0, 1.0, 1.0)"
"BoxCollider: SolidCollider, 'offset': (0.0, 0.0), 'size': (0.8, 0.8), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"

"Placeable, 02_Plank2(Clone): pos: (-11.0, -8.5, 0.0), scale: (1.0, 1.0, 1.0)"
"BoxCollider: SolidCollider, 'offset': (0.0, 0.0), 'size': (2.0, 1.0), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"

"Placeable, 11_1x1 Spike Block(Clone): pos: (-12.0, -7.0, 0.0), scale: (1.0, 1.0, 1.0)"
"BoxCollider: SolidCollider, 'offset': (0.0, 0.0), 'size': (0.8, 0.8), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"

"Placeable, 11_1x1 Spike Block(Clone): pos: (-10.0, -7.0, 0.0), scale: (1.0, 1.0, 1.0)"
"BoxCollider: SolidCollider, 'offset': (0.0, 0.0), 'size': (0.8, 0.8), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"

"Placeable, 105_SetPiece1x14(Clone): pos: (-9.0, -10.0, 0.0), scale: (1.0, 1.0, 1.0)"
"BoxCollider: SolidCollider, 'offset': (8.5, 0.0), 'size': (16.0, 1.0), 'scale': (1.0, 1.0, 1.0), localPos: (-8.0, 0.0, 0.0)"
"BoxCollider: RequiredCollider, 'offset': (0.0, 0.0), 'size': (0.3, 0.3), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, -0.8, 0.0)"
"BoxCollider: Collider, 'offset': (0.0, -0.3), 'size': (0.8, 0.4), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: PlacementColliderAtt, 'offset': (0.0, -0.6), 'size': (0.5, 0.2), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"

"GoalBlock, GoalBlock: pos: (18.0, -10.0, 0.0), scale: (1.0, 1.0, 1.0)"
"BoxCollider: SolidCollider, 'offset': (0.0, 0.0), 'size': (1.0, 1.0), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: GoalCollider, 'offset': (0.9, 2.2), 'size': (3.9, 4.0), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"

"Placeable, StartPlank: pos: (-18.5, -10.0, 0.0), scale: (1.0, 1.0, 1.0)"
"BoxCollider: SolidCollider, 'offset': (0.0, 0.0), 'size': (4.0, 1.0), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: StartZone, 'offset': (0.0, 0.4), 'size': (3.8, 4.5), 'scale': (1.0, 1.0, 1.0), localPos: (-0.9, -0.3, 0.0)"

"Character, RACCOON: pos: (-17.9, -9.1, 0.0), scale: (1.3, 1.3, 1.3)"
"BoxCollider: RACCOON, 'offset': (0.0, 0.5), 'size': (1.0, 1.5), 'scale': (1.3, 1.3, 1.3), localPos: (-17.9, -9.1, 0.0)"
"BoxCollider: UpperBody, 'offset': (0.0, 0.5), 'size': (0.5, 0.6), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"CapsuleCollider: UpperBody, 'offset': (0.0, 0.7), 'size': (0.7, 0.3), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: UpperBody, 'offset': (0.0, 0.7), 'size': (0.6, 0.3), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"CapsuleCollider: LowerBody, 'offset': (0.0, -0.2), 'size': (0.7, 0.3), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"CapsuleCollider: LowerBody, 'offset': (0.0, 0.2), 'size': (0.7, 0.3), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: LowerBody, 'offset': (0.0, 0.0), 'size': (0.6, 0.3), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: LowerBody, 'offset': (0.0, -0.2), 'size': (0.6, 0.3), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: FeetPhysicsSensor, 'offset': (0.0, -0.3), 'size': (0.5, 0.1), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: Head, 'offset': (0.0, 0.6), 'size': (0.4, 0.3), 'scale': (1.0, 1.3, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: HazardHead, 'offset': (0.0, 0.6), 'size': (0.6, 0.3), 'scale': (1.0, 1.3, 1.0), localPos: (0.0, 0.0, 0.0)"
"CircleCollider: DeadCollider, 'offset': (0.0, 0.0), 'radius': 0.3, 'scale': (1.0, 1.0, 1.0), localPos: (0.1, 0.4, 0.0)"
"BoxCollider: UpperBodyTrigger, 'offset': (0.0, 0.5), 'size': (0.5, 0.6), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
"BoxCollider: LowerBodyTrigger, 'offset': (0.0, 0.0), 'size': (0.5, 0.5), 'scale': (1.0, 1.0, 1.0), localPos: (0.0, 0.0, 0.0)"
 */