// ASHFALL — interface for anything the player can focus and use (carts, valves,
// levers, doors, citizens). Implemented by UInteractableComponent's owner or BPs.
#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "Interactable.generated.h"

UINTERFACE(MinimalAPI, Blueprintable)
class UInteractable : public UInterface
{
	GENERATED_BODY()
};

class IInteractable
{
	GENERATED_BODY()

public:
	/** Use this interactable. */
	UFUNCTION(BlueprintNativeEvent, Category = "Interaction")
	void Interact(AActor* Instigator);
	virtual void Interact_Implementation(AActor* Instigator) {}

	/** Short prompt shown when the player focuses this (e.g. "Shift the cart"). */
	UFUNCTION(BlueprintNativeEvent, Category = "Interaction")
	FText GetInteractionPrompt() const;
	virtual FText GetInteractionPrompt_Implementation() const { return FText::GetEmpty(); }
};
