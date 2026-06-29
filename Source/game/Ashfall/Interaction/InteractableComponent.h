// ASHFALL — drop-on-any-actor interaction. On use it sets a temporal causal flag
// (the Zenith intervention) so the change ripples into the Fall outcome.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InteractableComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnInteracted, UInteractableComponent*, Component, AActor*, Instigator);

UCLASS(ClassGroup = (Ashfall), meta = (BlueprintSpawnableComponent))
class UInteractableComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UInteractableComponent();

	/** Prompt shown when focused (e.g. "Shift the cart clear of the stair"). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interaction")
	FText Prompt;

	/** Causal flag set on the temporal subsystem when used (the ripple key). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interaction")
	FName CausalFlag;

	/** Value the flag is set to when used. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interaction")
	bool bFlagValue = true;

	/** If true, the interactable can only be used once. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interaction")
	bool bSingleUse = true;

	/** True once used (for single-use interactables). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Interaction")
	bool bUsed = false;

	/** Fired when successfully used. */
	UPROPERTY(BlueprintAssignable, Category = "Interaction")
	FOnInteracted OnInteracted;

	/** Attempt to use; sets the causal flag and broadcasts. Returns false if spent. */
	UFUNCTION(BlueprintCallable, Category = "Interaction")
	bool TryInteract(AActor* Instigator);
};
