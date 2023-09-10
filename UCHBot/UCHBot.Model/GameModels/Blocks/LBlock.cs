namespace UCHBot.Model.GameModels.Blocks;

[DebuggerDisplay("LBlock: {_block1}, {_block2}")]
public class LBlock : IBlock
{
    private static readonly Vector2 Block1Size = new(4, 1);
    private static readonly Vector2 Block2Size = new(1, 4);

    private static readonly Dictionary<int, Vector2> Block1Offsets = new()
    {
        [0] = new Vector2(-1.5f, 0.5f),
        [90] = new Vector2(-1.5f, -2.5f),
        [180] = new Vector2(-1.5f, -2.5f),
        [270] = new Vector2(-1.5f, 0.5f)
    };
    private static readonly Dictionary<int, Vector2> Block2Offsets = new()
    {
        [0] = new Vector2(-1.5f, -2.5f),
        [90] = new Vector2(-1.5f, -2.5f),
        [180] = new Vector2(1.5f, -2.5f),
        [270] = new Vector2(1.5f, -2.5f),
    };

    private readonly StaticBlock _block1;
    private readonly StaticBlock _block2;

    public LBlock(int sceneId, int? parentId, int blockId, Vector2 position, int rotation)
    {
	    Vector2 offset1 = Block1Offsets[rotation];
	    Vector2 offset2 = Block2Offsets[rotation];

        _block1 = new StaticBlock(sceneId, parentId, blockId, position + offset1, Block1Size, CollisionType.Block);
        _block2 = new StaticBlock(sceneId, parentId, blockId, position + offset2, Block2Size, CollisionType.Block);
    }

    public static bool TryParse(XmlNode xmlNode, out IBlock block)
    {
        block = null;

        if (xmlNode.Name != "block")
            return false;

        int sceneId = Block.GetSceneId(xmlNode);
        int? parentId = Block.GetParentId(xmlNode);
        int blockId = Block.GetBlockId(xmlNode);

        if (blockId != 8)
            return false;

        int rotation = Block.GetRotation(xmlNode);
        Vector2 position = Block.GetPosition(xmlNode);

        block = new LBlock(sceneId, parentId, blockId, position, rotation);
        return true;
    }

    public IEnumerable<BlockSurface> GetSurfaces(Bounds other)
    {
        return _block1.GetSurfaces(other)
            .Concat(_block2.GetSurfaces(other));
    }

    public IEnumerable<StaticBlock> GetStaticBlocks()
    {
        return new[] { _block1, _block2 };
    }
}