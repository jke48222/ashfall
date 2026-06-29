// ASHFALL — UInteractableComponent implementation.
#include "InteractableComponent.h"
#include "TemporalSubsystem.h"
#include "Engine/World.h"
#include "game.h"

UInteractableComponent::UInteractableComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

bool UInteractableComponent::TryInteract(AActor* Instigator)
{
	if (bUsed && bSingleUse)
	{
		return false;
	}
	bUsed = true;

	if (!CausalFlag.IsNone())
	{
		if (const UWorld* World = GetWorld())
		{
			if (UTemporalSubsystem* Temporal = World->GetSubsystem<UTemporalSubsystem>())
			{
				Temporal->SetCausalFlag(CausalFlag, bFlagValue);
				UE_LOG(Loggame, Log, TEXT("[Interact] %s -> causal flag '%s'=%d"),
					*GetOwner()->GetName(), *CausalFlag.ToString(), bFlagValue ? 1 : 0);
			}
		}
	}

	OnInteracted.Broadcast(this, Instigator);
	return true;
}
