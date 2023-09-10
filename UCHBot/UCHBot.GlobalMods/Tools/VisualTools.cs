using UnityEngine;

namespace UCHBot.GlobalMods.Tools;

public static class VisualTools
{
	private const float BorderWidth = 0.01f;

	public static GameObject CreateRectangle(float x, float y, float width, float height, Color color, bool onTop)
	{
		// Create a new game object and add necessary components
		GameObject rectangleObject = new("Rectangle")
		{
			transform =
			{
				position = new Vector3(x - BorderWidth, y - BorderWidth, 0),
				localScale = new Vector3(width + 2 * BorderWidth, height + 2 * BorderWidth)
			}
		};

		MeshFilter meshFilter = rectangleObject.AddComponent<MeshFilter>();
		MeshRenderer meshRenderer = rectangleObject.AddComponent<MeshRenderer>();
		if(onTop)
			meshRenderer.sortingLayerName = "Player";

		// Create a mesh for the rectangle
		Mesh mesh = new()
		{
			vertices = new Vector3[]
			{
				new(0f, 0f), // Bottom-left vertex
				new(1f, 0f), // Bottom-right vertex
				new(0f, 1f), // Top-left vertex
				new(1f, 1f) // Top-right vertex
			},
			triangles = new int[] { 0, 2, 1, 2, 3, 1 } // Triangle indices
		};
		mesh.RecalculateNormals();

		// Assign the mesh to the mesh filter
		meshFilter.mesh = mesh;

		//Shaders.k_Runtime
		// Set the material and color of the mesh renderer
		meshRenderer.material = new Material(Shader.Find("Sprites/Default"))
		{
			color = color
		};
		return rectangleObject;
	}
}