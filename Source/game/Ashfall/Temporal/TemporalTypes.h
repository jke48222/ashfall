// ASHFALL — core temporal types. The two-state time mechanic lives and dies here.
#pragma once

#include "CoreMinimal.h"
#include "TemporalTypes.generated.h"

class UMaterialInterface;

/** The two moments of every location in ASHFALL. */
UENUM(BlueprintType)
enum class ETimeState : uint8
{
	Zenith UMETA(DisplayName = "Zenith (golden age)"),
	Fall   UMETA(DisplayName = "Fall (collapse)")
};

/**
 *  How a single actor should look/behave in one time state. A
 *  UTemporalStateComponent holds one of these per state and applies the active
 *  one when the world toggles.
 */
USTRUCT(BlueprintType)
struct FTemporalStateConfig
{
	GENERATED_BODY()

	/** Whether the owner is visible & collidable in this state. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal")
	bool bVisible = true;

	/** Local-space delta from the captured base transform applied in this state
	 *  (e.g. a cart that has rolled, a beam that has fallen). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal")
	FTransform LocalOffset = FTransform::Identity;

	/** If set, this material is applied to every primitive of the owner in this state. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal")
	TSoftObjectPtr<UMaterialInterface> MaterialOverride;

	/** Whether the owner's root simulates physics in this state. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Temporal")
	bool bSimulatePhysics = false;
};
