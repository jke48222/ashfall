// ASHFALL — AAshfallGameMode implementation.
#include "AshfallGameMode.h"
#include "AshfallCharacter.h"
#include "AshfallPlayerController.h"

AAshfallGameMode::AAshfallGameMode()
{
	// C++ defaults; a Blueprint child (set up in M3) supplies the visual pawn/HUD.
	DefaultPawnClass = AAshfallCharacter::StaticClass();
	PlayerControllerClass = AAshfallPlayerController::StaticClass();
}
