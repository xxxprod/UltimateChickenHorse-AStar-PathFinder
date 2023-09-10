namespace UCHBot.Model.GameModels;

[Flags]
public enum CollisionType
{
	Block =             0x01,
	Goal =              0x02,
	Death =             0x04,
	LevelBorder =       0x08,
	LeftBorder =        0x10 | LevelBorder,
	RightBorder =       0x20 | LevelBorder,
	TopBorder =         0x40 | LevelBorder,
	BottomBorder =      0x80 | LevelBorder,
	DeathPit =          Death | BottomBorder
}