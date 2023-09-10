namespace UCHBot.Model.GameModels.Blocks;

[DebuggerDisplay("BarrelBlock[{BlockId}]: {Bounds}")]
public class BarrelBlock : StaticBlock
{
    private static readonly Vector2 Size = new(2, 2);

    private static readonly Vector2 PositionOffset = new(-0.5f, -1.5f);


    public BarrelBlock(int sceneId, int? parentId, int blockId, Vector2 position) : base(sceneId, parentId, blockId, position, Size, CollisionType.Block)
    {
    }

    public new static bool TryParse(XmlNode xmlNode, out IBlock block)
    {
        block = null;

        if (xmlNode.Name != "block")
            return false;

        int sceneId = GetSceneId(xmlNode);
        int? parentId = GetParentId(xmlNode);
        int blockId = GetBlockId(xmlNode);

        if (blockId is not 6)
            return false;

        Vector2 position = GetPosition(xmlNode);
        Vector2 offset = PositionOffset;

        block = new BarrelBlock(sceneId, parentId, blockId, position + offset);
        return true;
    }

    public override IEnumerable<BlockSurface> GetSurfaces(Bounds other)
    {
        return Equals(other, default(Bounds))
            ? Surfaces
            : Surfaces.Where(s => s.Bounds.Intersects(other, 0));
    }

    public override IEnumerable<StaticBlock> GetStaticBlocks()
    {
        return new[] { this };
    }
}