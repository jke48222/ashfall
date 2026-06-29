// ASHFALL — player controller. Adds a dev console command to flip time state.
#pragma once

#include "CoreMinimal.h"
#include "gamePlayerController.h"
#include "AshfallPlayerController.generated.h"

UCLASS()
class AAshfallPlayerController : public AgamePlayerController
{
	GENERATED_BODY()

public:
	/** Console command: flips Zenith <-> Fall (developer/testing aid). */
	UFUNCTION(Exec)
	void ToggleTimeState();
};
