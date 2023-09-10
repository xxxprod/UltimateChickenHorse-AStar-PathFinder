namespace UCHBot.Shared.Modules;

public static class CharacterSelectorModule
{
    public static bool SelectCharacter(Character.Animals animal)
    {
        if (LobbyManager.instance?.GetLobbyPlayers()?.First() == null)
            return false;
        
        UCHTools.Log($"Start selecting animal {animal}");

        LobbyPlayer lobbyPlayer = LobbyManager.instance.GetLobbyPlayers().First();

        Character character = Character.AllCharacters.First(a => a.CharacterSprite == animal);

        lobbyPlayer.RequestPickCharacter(character);

        UCHTools.Log($"Finished selecting animal {animal}");

        return true;
    }
}