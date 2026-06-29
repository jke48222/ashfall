// ASHFALL — drives a single actor between its Zenith and Fall configurations.
// Attach to any structural/dressing actor; the subsystem pushes state changes.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TemporalTypes.h"
#include "TemporalStateComponent.generated.h"

class UTemporalSubsystem;

UCLASS(ClassGroup = (Ashfall), meta = (BlueprintSpawnableComponent))
class UTemporalStateComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UTemporalStateComponent();

	/** Owner's appearance/behaviour in the golden age. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal")
	FTemporalStateConfig Zenith;

	/** Owner's appearance/behaviour during the collapse. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal")
	FTemporalStateConfig Fall;

	/** If > 0 the transform blends over this many seconds on change; else snaps. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal", meta = (ClampMin = 0, Units = "s"))
	float BlendTime = 0.35f;

	const FTemporalStateConfig& ConfigFor(ETimeState State) const
	{
		return State == ETimeState::Fall ? Fall : Zenith;
	}

	/** Applies the configuration for State (called by the subsystem). */
	UFUNCTION(BlueprintCallable, Category = "Temporal")
	void ApplyState(ETimeState State, bool bImmediate);

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Resolves the owner's world target transform for State from the captured base. */
	FTransform TargetTransformFor(ETimeState State) const;

	void ApplyVisualsAndPhysics(const FTemporalStateConfig& Config) const;

	UPROPERTY()
	TWeakObjectPtr<UTemporalSubsystem> Subsystem;

	/** Owner's world transform captured at BeginPlay; offsets are relative to this. */
	FTransform BaseWorldTransform;

	// Transform blend bookkeeping.
	bool bBlending = false;
	float BlendElapsed = 0.0f;
	FTransform BlendFrom;
	FTransform BlendTo;
};
