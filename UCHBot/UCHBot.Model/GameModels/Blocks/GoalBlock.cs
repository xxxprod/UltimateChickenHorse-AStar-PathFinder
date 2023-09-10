namespace UCHBot.Model.GameModels.Blocks;

[DebuggerDisplay("Goal: {_goalArea}")]
public class GoalBlock : IBlock
{
    private static readonly Vector2 GoalBlockSize = new(1, 1);
    private static readonly Vector2 GoalAreaSize = new(4, 4);

    private static readonly Dictionary<int, Vector2> GoalBlockOffsets = new()
    {
        [0] = new Vector2(0, -1),
        [90] = new Vector2(0, -1),
        [180] = new Vector2(0, -1),
        [270] = new Vector2(0, -1)
    };
    private static readonly Dictionary<int, Vector2> GoalAreaOffsets = new()
    {
        [0] = new Vector2(-2, 0),
        [90] = new Vector2(-4, -3),
        [180] = new Vector2(-1, -5),
        [270] = new Vector2(1, -2)
    };

    private readonly StaticBlock _goalBlock;
    private readonly StaticBlock _goalArea;

    public GoalBlock(int sceneId, int? parentId, int blockId, Vector2 position, int rotation)
    {
	    Vector2 offset1 = GoalBlockOffsets[rotation];
	    Vector2 offset2 = GoalAreaOffsets[rotation];

	    _goalBlock = new StaticBlock(sceneId, parentId, blockId, position + offset1, GoalBlockSize, CollisionType.Block);
	    _goalArea = new StaticBlock(sceneId, parentId, blockId, position + offset2, GoalAreaSize, CollisionType.Goal);
    }

    public Bounds Bounds => _goalArea.Bounds;

    public static bool TryParse(XmlNode xmlNode, out IBlock block)
    {
        block = null;

        if (xmlNode.Name != "block")
            return false;

        int sceneId = Block.GetSceneId(xmlNode);
        int? parentId = Block.GetParentId(xmlNode);
        int blockId = Block.GetBlockId(xmlNode);

        if (blockId != 39)
            return false;

        int rotation = Block.GetRotation(xmlNode);
        Vector2 position = Block.GetPosition(xmlNode);

        block = new GoalBlock(sceneId, parentId, blockId, position, rotation);
        return true;
    }

    public IEnumerable<BlockSurface> GetSurfaces(Bounds other)
    {
        return _goalBlock.GetSurfaces(other)
            .Concat(_goalArea.GetSurfaces(other));
    }

    public IEnumerable<StaticBlock> GetStaticBlocks()
    {
        return new[] { _goalBlock, _goalArea };
    }
}