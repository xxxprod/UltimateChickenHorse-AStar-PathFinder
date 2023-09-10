using Newtonsoft.Json;

namespace UCHBot.Model.GameModels.Blocks;

[DebuggerDisplay("Block[{BlockId}]: {Bounds}")]
public class StaticBlock : Block
{
    private static readonly Dictionary<int, Vector2> BlockSizes = new()
    {
        [40] = new Vector2(1, 1),
        [41] = new Vector2(2, 1),
        [42] = new Vector2(3, 1),
        [43] = new Vector2(4, 1),
        [44] = new Vector2(8, 1),
        [45] = new Vector2(16, 1),
        [46] = new Vector2(4, 2),
        [47] = new Vector2(2, 2),
        [48] = new Vector2(4, 4),
        [49] = new Vector2(8, 8),
        [50] = new Vector2(6, 16)
    };

    private static readonly Dictionary<int, Dictionary<int, Vector2>> PositionOffsets = new()
    {
        [0] = new Dictionary<int, Vector2>
        {
            [40] = new(0, -1),
            [41] = new(0, -1),
            [42] = new(-1, -1),
            [43] = new(-1, -1),
            [44] = new(-4, -1),
            [45] = new(-7, -1),
            [46] = new(-1, -2),
            [47] = new(0, -2),
            [48] = new(-1, -3),
            [49] = new(-3, -5),
            [50] = new(-2, -9)
        },
        [90] = new Dictionary<int, Vector2>
        {
            [40] = new(0, -1),
            [41] = new(0, -1),
            [42] = new(0, -2),
            [43] = new(0, -2),
            [44] = new(0, -5),
            [45] = new(0, -8),
            [46] = new(0, -2),
            [47] = new(0, -1),
            [48] = new(-1, -2),
            [49] = new(-3, -4),
            [50] = new(-7, -3),
        },
        [180] = new Dictionary<int, Vector2>
        {
            [40] = new(0, -1),
            [41] = new(-1, -1),
            [42] = new(-1, -1),
            [43] = new(-2, -1),
            [44] = new(-3, -1),
            [45] = new(-8, -1),
            [46] = new(-2, -1),
            [47] = new(-1, -1),
            [48] = new(-2, -2),
            [49] = new(-4, -4),
            [50] = new(-3, -8)
        },
        [270] = new Dictionary<int, Vector2>
        {
            [40] = new(0, -1),
            [41] = new(0, -2),
            [42] = new(0, -2),
            [43] = new(0, -3),
            [44] = new(0, -4),
            [45] = new(0, -9),
            [46] = new(-1, -3),
            [47] = new(-1, -2),
            [48] = new(-2, -3),
            [49] = new(-4, -5),
            [50] = new(-8, -4),
        }
    };


    public StaticBlock(int sceneId, int? parentId, int blockId, Vector2 position, Vector2 size, CollisionType collisionType) : base(sceneId, parentId, blockId)
    {
        CollisionType = collisionType;
        Bounds = new Bounds(position, size).Translate(new Vector2(-0.5f, 0.5f));
        Surfaces = new[]
        {
            new BlockSurface(this, BlockFace.Left, collisionType),
            new BlockSurface(this, BlockFace.Right, collisionType),
            new BlockSurface(this, BlockFace.Top, collisionType)
        };
    }

    public Bounds Bounds { get; set; }
    public CollisionType CollisionType { get; }
    
    [JsonIgnore]
    public BlockSurface[] Surfaces { get; protected set; }

    public static bool TryParse(XmlNode xmlNode, out IBlock block)
    {
        block = null;

        if (xmlNode.Name != "block")
            return false;

        int sceneId = GetSceneId(xmlNode);
        int? parentId = GetParentId(xmlNode);
        int blockId = GetBlockId(xmlNode);

        if (!BlockSizes.TryGetValue(blockId, out Vector2 size))
            return false;

        int rotation = GetRotation(xmlNode);
        bool isRotated = rotation is 90 or 270;

        if (isRotated)
            size = new Vector2(size.Y, size.X);

        Vector2 position = GetPosition(xmlNode);
        Vector2 offset = PositionOffsets[rotation][blockId];

        block = new StaticBlock(sceneId, parentId, blockId, position + offset, size, CollisionType.Block);
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