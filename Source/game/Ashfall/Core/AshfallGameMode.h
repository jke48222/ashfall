// ASHFALL — game mode wiring the Chronomason pawn and controller.
#pragma once

#include "CoreMinimal.h"
#include "gameGameMode.h"
#include "AshfallGameMode.generated.h"

UCLASS()
class AAshfallGameMode : public AgameGameMode
{
	GENERATED_BODY()

public:
	AAshfallGameMode();

protected:
	virtual void BeginPlay() override;

	/** Auto-capture sequence (Zenith shot -> toggle -> Fall shot -> quit), driven
	 *  by the `-AshfallAutoShot` command-line flag for headless milestone renders. */
	void AutoShotStep();

	int32 AutoShotIndex = 0;
};
