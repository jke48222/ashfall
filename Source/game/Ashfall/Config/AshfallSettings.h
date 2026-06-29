// ASHFALL — project-level tuning, surfaced in Project Settings -> Game -> Ashfall.
#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "AshfallSettings.generated.h"

UCLASS(config = Game, defaultconfig, meta = (DisplayName = "Ashfall"))
class UAshfallSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	/** Default seconds between temporal toggles for the player. */
	UPROPERTY(EditAnywhere, config, Category = "Temporal", meta = (ClampMin = 0, Units = "s"))
	float DefaultToggleCooldown = 0.5f;

	/** Number of citizens that must be saved to avert collapse in the slice. */
	UPROPERTY(EditAnywhere, config, Category = "Slice", meta = (ClampMin = 1))
	int32 CitizensToSave = 6;

	virtual FName GetCategoryName() const override { return FName(TEXT("Game")); }
};
