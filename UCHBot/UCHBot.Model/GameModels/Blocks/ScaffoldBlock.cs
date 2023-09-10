namespace UCHBot.Model.GameModels.Blocks;

[DebuggerDisplay("ScaffoldBlock: {_block1},{_block2}")]
public class ScaffoldBlock : IBlock
{
    private static readonly Vector2 Block1Size = new(1, 1);
    private static readonly Vector2 Block2Size = new(1, 1);

    private static readonly Dictionary<int, Vector2> Block1Offsets = new()
    {
        [0] = new Vector2(0, 3),
        [90] = new Vector2(-4, -1),
        [180] = new Vector2(0, -1),
        [270] = new Vector2(0, -1)
    };
    private static readonly Dictionary<int, Vector2> Block2Offsets = new()
    {
        [0] = new Vector2(0, -1),
        [90] = new Vector2(0, -1),
        [180] = new Vector2(0, -5),
        [270] = new Vector2(4, -1),
    };

    private readonly StaticBlock _block1;
    private readonly StaticBlock _block2;

    public ScaffoldBlock(int sceneId, int? parentId, int blockId, Vector2 position, int rotation)
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

        if (blockId is not (56 or 60))
            return false;

        int rotation = Block.GetRotation(xmlNode);
        Vector2 position = Block.GetPosition(xmlNode);

        block = new ScaffoldBlock(sceneId, parentId, blockId, position, rotation);
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