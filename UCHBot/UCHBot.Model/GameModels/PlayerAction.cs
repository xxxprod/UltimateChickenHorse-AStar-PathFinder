namespace UCHBot.Model.GameModels;

[Flags]
public enum PlayerAction
{
    None            = 0x00,
    Left            = 0x01,
    Right           = 0x02,
    Up              = 0x04,
    Down            = 0x08,
    Jump            = 0x10,
    Sprint          = 0x20
}