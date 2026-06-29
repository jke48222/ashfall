// ASHFALL — UTemporalSubsystem implementation.
#include "TemporalSubsystem.h"
#include "TemporalStateComponent.h"
#include "game.h"

void UTemporalSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	CurrentState = ETimeState::Zenith;
}

void UTemporalSubsystem::Deinitialize()
{
	RegisteredComponents.Reset();
	CausalFlags.Reset();
	Super::Deinitialize();
}

bool UTemporalSubsystem::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Game
		|| WorldType == EWorldType::PIE
		|| WorldType == EWorldType::Editor
		|| WorldType == EWorldType::EditorPreview;
}

void UTemporalSubsystem::SetState(ETimeState NewState, bool bForce)
{
	if (NewState == CurrentState && !bForce)
	{
		return;
	}

	CurrentState = NewState;
	UE_LOG(Loggame, Log, TEXT("[Temporal] State -> %s"),
		CurrentState == ETimeState::Fall ? TEXT("Fall") : TEXT("Zenith"));

	BroadcastState(/*bImmediate*/ false);
}

void UTemporalSubsystem::RequestToggle()
{
	SetState(CurrentState == ETimeState::Zenith ? ETimeState::Fall : ETimeState::Zenith);
}

void UTemporalSubsystem::BroadcastState(bool bImmediate)
{
	// Push to every registered component, pruning anything that has gone stale.
	for (int32 i = RegisteredComponents.Num() - 1; i >= 0; --i)
	{
		if (UTemporalStateComponent* Comp = RegisteredComponents[i].Get())
		{
			Comp->ApplyState(CurrentState, bImmediate);
		}
		else
		{
			RegisteredComponents.RemoveAtSwap(i);
		}
	}

	OnTimeStateChanged.Broadcast(CurrentState);
}

void UTemporalSubsystem::RegisterComponent(UTemporalStateComponent* Component)
{
	if (!Component)
	{
		return;
	}
	RegisteredComponents.AddUnique(Component);
	// Snap the newcomer to the current state immediately.
	Component->ApplyState(CurrentState, /*bImmediate*/ true);
}

void UTemporalSubsystem::UnregisterComponent(UTemporalStateComponent* Component)
{
	RegisteredComponents.RemoveAllSwap([Component](const TWeakObjectPtr<UTemporalStateComponent>& Ptr)
	{
		return !Ptr.IsValid() || Ptr.Get() == Component;
	});
}

void UTemporalSubsystem::SetCausalFlag(FName Flag, bool bSet)
{
	if (Flag.IsNone())
	{
		return;
	}
	if (bSet)
	{
		CausalFlags.Add(Flag);
	}
	else
	{
		CausalFlags.Remove(Flag);
	}
}

bool UTemporalSubsystem::HasCausalFlag(FName Flag) const
{
	return CausalFlags.Contains(Flag);
}
