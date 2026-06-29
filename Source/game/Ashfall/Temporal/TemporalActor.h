// ASHFALL — interface for bespoke actors that react to time-state changes
// (puzzle objects, scripted set-pieces). Most static dressing uses
// UTemporalStateComponent instead; this is for actors with custom logic.
#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "TemporalTypes.h"
#include "TemporalActor.generated.h"

UINTERFACE(MinimalAPI, Blueprintable)
class UTemporalActor : public UInterface
{
	GENERATED_BODY()
};

class ITemporalActor
{
	GENERATED_BODY()

public:
	/** Called by UTemporalSubsystem whenever the active time state changes. */
	UFUNCTION(BlueprintNativeEvent, Category = "Temporal")
	void OnTimeStateChanged(ETimeState NewState);
	virtual void OnTimeStateChanged_Implementation(ETimeState NewState) {}
};
