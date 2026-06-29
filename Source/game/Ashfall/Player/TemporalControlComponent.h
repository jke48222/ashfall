// ASHFALL — player-side helper that owns the toggle verb (cooldown, focus hook).
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TemporalTypes.h"
#include "TemporalControlComponent.generated.h"

class UTemporalSubsystem;

UCLASS(ClassGroup = (Ashfall), meta = (BlueprintSpawnableComponent))
class UTemporalControlComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UTemporalControlComponent();

	/** Flips the world's time state if the cooldown has elapsed. Returns true if it toggled. */
	UFUNCTION(BlueprintCallable, Category = "Temporal")
	bool RequestToggle();

	UFUNCTION(BlueprintCallable, Category = "Temporal")
	ETimeState GetState() const;

	/** Minimum seconds between toggles. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal", meta = (ClampMin = 0, Units = "s"))
	float ToggleCooldown = 0.5f;

protected:
	UTemporalSubsystem* GetSubsystem() const;

	double LastToggleTime = -1000.0;
};
