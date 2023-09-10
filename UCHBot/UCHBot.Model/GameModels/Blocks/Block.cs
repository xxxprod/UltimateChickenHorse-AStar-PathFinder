namespace UCHBot.Model.GameModels.Blocks;

public abstract class Block : IBlock
{
    protected Block(int sceneId, int? parentId, int blockId)
    {
        SceneId = sceneId;
        ParentId = parentId;
        BlockId = blockId;
    }

    public int SceneId { get; }
    public int? ParentId { get; }
    public int BlockId { get; }

    public abstract IEnumerable<BlockSurface> GetSurfaces(Bounds other);

    public abstract IEnumerable<StaticBlock> GetStaticBlocks();

    public static int GetSceneId(XmlNode xmlNode)
    {
        return xmlNode.Attributes.GetInt("sceneID");
    }

    public static int GetBlockId(XmlNode xmlNode)
    {
        return xmlNode.Attributes.GetInt("blockID");
    }

    public static int? GetParentId(XmlNode xmlNode)
    {
        return xmlNode.Attributes.GetNullableInt("parentID");
    }

    public static int? GetMainId(XmlNode xmlNode)
    {
        return xmlNode.Attributes.GetNullableInt("mainID");
    }

    public static Vector2 GetPosition(XmlNode xmlNode)
    {
        Debug.Assert(xmlNode.Attributes != null, "xmlNode.Attributes != null");

        float x = xmlNode.Attributes.GetFloat("pX");
        float y = xmlNode.Attributes.GetFloat("pY");

        return new Vector2(x, y);
    }

    public static int GetRotation(XmlNode xmlNode)
    {
        Debug.Assert(xmlNode.Attributes != null, "xmlNode.Attributes != null");

        return xmlNode.Attributes.GetInt("rZ");
    }
}