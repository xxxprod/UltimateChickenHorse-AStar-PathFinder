namespace UCHBot.Model.GameModels.Blocks;

public class WoodBlock : StaticBlock
{
    private static readonly Dictionary<int, Vector2> BlockSizes = new()
    {
        [0] = new Vector2(1, 1),
        [1] = new Vector2(2, 1),
        [2] = new Vector2(3, 1),
        [3] = new Vector2(4, 1),
        [4] = new Vector2(5, 1),
        [5] = new Vector2(6, 1),
    };

    private static readonly Dictionary<int, Dictionary<int, Vector2>> PositionOffsets = new()
    {
        [0] = new Dictionary<int, Vector2>
        {
            [0] = new(0, -1),
            [1] = new(-0.5f, -1),
            [2] = new(-1, -1),
            [3] = new(-1.5f, -1),
            [4] = new(-2, -1),
            [5] = new(-2.5f, -1),
        },
        [90] = new Dictionary<int, Vector2>
        {
            [0] = new(0, -1),
            [1] = new(0, -1.5f),
            [2] = new(0, -2),
            [3] = new(0, -2.5f),
            [4] = new(0, -3),
            [5] = new(0, -3.5f),
        },
        [180] = new Dictionary<int, Vector2>
        {
            [0] = new(0, -1),
            [1] = new(-0.5f, -1),
            [2] = new(-1, -1),
            [3] = new(-1.5f, -1),
            [4] = new(-2, -1),
            [5] = new(-2.5f, -1),
        },
        [270] = new Dictionary<int, Vector2>
        {
            [0] = new(0, -1),
            [1] = new(0, -1.5f),
            [2] = new(0, -2),
            [3] = new(0, -2.5f),
            [4] = new(0, -3),
            [5] = new(0, -3.5f),
        }
    };
    public WoodBlock(int sceneId, int? parentId, int blockId, Vector2 position, Vector2 size, CollisionType collisionType) : base(sceneId, parentId, blockId, position, size, collisionType)
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

        if (!BlockSizes.TryGetValue(blockId, out Vector2 size))
            return false;

        int rotation = GetRotation(xmlNode);
        bool isRotated = rotation is 90 or 270;

        if (isRotated)
            size = new Vector2(size.Y, size.X);

        Vector2 position = GetPosition(xmlNode);
        Vector2 offset = PositionOffsets[rotation][blockId];

        block = new WoodBlock(sceneId, parentId, blockId, position + offset, size, CollisionType.Block);
        return true;
    }
}