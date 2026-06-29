// ASHFALL — a static-mesh actor that morphs between Zenith and Fall states.
// Spawned by the level builder; its UTemporalStateComponent auto-registers with
// the world's UTemporalSubsystem and applies the active state on toggle.
#pragma once

#include "CoreMinimal.h"
#include "Engine/StaticMeshActor.h"
#include "TemporalProp.generated.h"

class UTemporalStateComponent;

UCLASS()
class ATemporalProp : public AStaticMeshActor
{
	GENERATED_BODY()

public:
	ATemporalProp();

	/** Drives this prop's Zenith/Fall appearance (configure Zenith/Fall on it). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Temporal")
	TObjectPtr<UTemporalStateComponent> Temporal;
};
