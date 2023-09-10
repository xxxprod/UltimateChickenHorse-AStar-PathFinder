using Newtonsoft.Json;

namespace UCHBot.Model.GameModels.Blocks;

[DebuggerDisplay("{Face}, {CollisionType}, {Bounds}")]
public class BlockSurface
{
    public BlockSurface(StaticBlock block, BlockFace face, CollisionType collisionType) :
        this(face, collisionType, GetBounds(block, face))
    {
    }

    [JsonConstructor]
    public BlockSurface(BlockFace face, CollisionType collisionType, Bounds bounds)
    {
        Face = face;
        CollisionType = collisionType;
        Bounds = bounds;
    }

    public BlockFace Face { get; }
    public CollisionType CollisionType { get; }
    public Bounds Bounds { get; }

    private static Bounds GetBounds(StaticBlock block, BlockFace face)
    {
        Bounds b = block.Bounds;
        return face switch
        {
            BlockFace.Top => new Bounds(b.Left, b.Top, b.Size.X, 0),
            BlockFace.Left => new Bounds(b.Left, b.Bottom, 0, b.Size.Y),
            BlockFace.Right => new Bounds(b.Right, b.Bottom, 0, b.Size.Y),
            _ => throw new ArgumentOutOfRangeException()
        };
    }
}