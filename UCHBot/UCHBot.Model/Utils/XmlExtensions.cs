using System.Globalization;

namespace UCHBot.Model.Utils;

public static class XmlExtensions
{
    public static IEnumerable<XmlNode> GetNodes(this XmlDocument xml, string xpath)
    {
        XmlNodeList xmlNodeList = xml.DocumentElement?.SelectNodes(xpath) ??
                                  throw new InvalidOperationException($"No nodes found at xpath {xpath}");

        return xmlNodeList.Cast<XmlNode>();
    }

    public static XmlNode GetNode(this XmlDocument xml, string xpath)
    {
        return xml.DocumentElement?.SelectSingleNode(xpath) ??
               throw new InvalidOperationException($"No node found at xpath {xpath}");
    }

    public static string GetString(this XmlAttributeCollection attributes, string attribute)
    {
        return attributes[attribute]?.Value;
    }

    public static int GetInt(this XmlAttributeCollection attributes, string attribute)
    {
        XmlAttribute xmlAttribute = attributes[attribute];

        if (string.IsNullOrEmpty(xmlAttribute?.Value))
            throw new InvalidOperationException($"Attribute {attribute} not found.");

        return Convert.ToInt32(xmlAttribute.Value, CultureInfo.InvariantCulture);
    }

    public static int? GetNullableInt(this XmlAttributeCollection attributes, string attribute)
    {
        XmlAttribute xmlAttribute = attributes[attribute];

        if (string.IsNullOrEmpty(xmlAttribute?.Value))
            return null;

        return Convert.ToInt32(xmlAttribute.Value, CultureInfo.InvariantCulture);
    }

    public static float GetFloat(this XmlAttributeCollection attributes, string attribute)
    {
        XmlAttribute xmlAttribute = attributes[attribute];
        if (string.IsNullOrEmpty(xmlAttribute?.Value))
            throw new InvalidOperationException($"Attribute {attribute} not found.");
        return Convert.ToSingle(xmlAttribute.Value, CultureInfo.InvariantCulture);
    }
}