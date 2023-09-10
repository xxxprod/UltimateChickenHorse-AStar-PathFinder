from utils.Rect import Rect
from utils.Vec import Vec


class PlayerConstants:
    playerWidth = 0.895
    playerHeight = 1.8
    playerRect = Rect([-playerWidth / 2, 0, playerWidth / 2, playerHeight])

    coyoteTime = 6
    maxSprintVelocity = 12.8
    sprintAcceleration = 0.768
    wallDeceleration = 1.25
    mediumSlideVelocity = -7

    wallCollisionPadding_up_top = 0.8
    wallCollisionPadding_up_bottom = 0.3

    wallCollisionPadding_down_top = 0.6
    wallCollisionPadding_down_bottom = 0.3
    wallVerticalCollisionPadding = 0.5

    groundCollisionPadding_left_right = 0.5

    maxWallContactVerticalVelocity = 12

    frameCollisionStartFrame = 3
    frameCollisionEndFrame = -3
    frameCollisionOffset = 0.05

    minGroundContactVelocity = -2
    minHorizontalContactVelocity = 1