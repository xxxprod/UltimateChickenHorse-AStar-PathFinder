using UnityEngine;

namespace UCHBot.Shared;

public class InputWrapper
{
    private static readonly Dictionary<KeyCode, bool> _keysPressed = new();

    public static bool? GetKeyPressed(KeyCode key)
    {
        return _keysPressed.TryGetValue(key, out bool value) ? value : (bool?) null;
    }
    
    public static void SetKeyPressed(KeyCode key, bool pressed)
    {
        if (pressed)
            _keysPressed[key] = true;
        else
            _keysPressed.Remove(key);
    }


    public static void Clear()
    {
        _keysPressed.Clear();
    }
}