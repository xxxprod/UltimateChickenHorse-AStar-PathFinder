namespace UCHBot.Model.GameModels.Blocks;

public class LevelBorderBlock : StaticBlock
{
	public const int BorderWidth = 0;
	public const int BorderLength = 100;

    public string Name { get; }

    public LevelBorderBlock(int sceneId, int? parentId, string name, int blockId, Vector2 position, Vector2 size, CollisionType collisionType) :
        base(sceneId, parentId, blockId, position, size, collisionType)
    {
        Name = name;
        Surfaces = Array.Empty<BlockSurface>();
    }

    public new static bool TryParse(XmlNode xmlNode, out IBlock block)
    {
        Debug.Assert(xmlNode.Attributes != null, "xmlNode.Attributes != null");

        block = null;

        int? parentId = GetParentId(xmlNode);

        Vector2 position = GetPosition(xmlNode);
        string name = xmlNode.Attributes.GetString("path");
        switch (name)
        {
            case "DeathPit":
                block = new LevelBorderBlock(-1, parentId, name, -1,
                    new Vector2(-BorderLength, position.Y + 4), 
                    new Vector2(2 * BorderLength, BorderWidth), 
                    CollisionType.DeathPit
                );
                return true;
            case "Ceiling":
                block = new LevelBorderBlock(-2, parentId, name, -1,
                    new Vector2(-BorderLength, position.Y - 5), 
                    new Vector2(2 * BorderLength, BorderWidth), 
                    CollisionType.TopBorder
                );
                return true;
            case "LeftWall":
                block = new LevelBorderBlock(-3, parentId, name, -1,
                    new Vector2(position.X + 5, -BorderLength), 
                    new Vector2(BorderWidth, 2 * BorderLength), 
                    CollisionType.LeftBorder
                );
                return true;
            case "RightWall":
                block = new LevelBorderBlock(-4, parentId, name, -1,
                    new Vector2(position.X - 4, -BorderLength), 
                    new Vector2(BorderWidth, 2 * BorderLength), 
                    CollisionType.RightBorder
                );
                return true;
            default:
                return false;
        }
    }
}