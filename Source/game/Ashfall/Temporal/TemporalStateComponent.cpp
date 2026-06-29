// ASHFALL — UTemporalStateComponent implementation.
#include "TemporalStateComponent.h"
#include "TemporalSubsystem.h"
#include "Components/PrimitiveComponent.h"
#include "Materials/MaterialInterface.h"
#include "GameFramework/Actor.h"

UTemporalStateComponent::UTemporalStateComponent()
{
	// Only ticks while a blend is in progress (enabled on demand).
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
}

void UTemporalStateComponent::BeginPlay()
{
	Super::BeginPlay();

	if (const AActor* Owner = GetOwner())
	{
		BaseWorldTransform = Owner->GetActorTransform();
	}

	if (UWorld* World = GetWorld())
	{
		Subsystem = World->GetSubsystem<UTemporalSubsystem>();
		if (Subsystem.IsValid())
		{
			// Registration snaps us to the current state immediately.
			Subsystem->RegisterComponent(this);
		}
	}
}

void UTemporalStateComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (Subsystem.IsValid())
	{
		Subsystem->UnregisterComponent(this);
	}
	Super::EndPlay(EndPlayReason);
}

FTransform UTemporalStateComponent::TargetTransformFor(ETimeState State) const
{
	const FTemporalStateConfig& Config = ConfigFor(State);
	const FTransform& Offset = Config.LocalOffset;

	// Apply the offset in the base's local frame: rotate the offset location by
	// the base rotation, compose rotations, multiply scales.
	FTransform Target;
	Target.SetLocation(BaseWorldTransform.GetLocation()
		+ BaseWorldTransform.TransformVectorNoScale(Offset.GetLocation()));
	Target.SetRotation(BaseWorldTransform.GetRotation() * Offset.GetRotation());
	Target.SetScale3D(BaseWorldTransform.GetScale3D() * Offset.GetScale3D());
	return Target;
}

void UTemporalStateComponent::ApplyVisualsAndPhysics(const FTemporalStateConfig& Config) const
{
	AActor* Owner = GetOwner();
	if (!Owner)
	{
		return;
	}

	Owner->SetActorHiddenInGame(!Config.bVisible);
	Owner->SetActorEnableCollision(Config.bVisible);

	TArray<UPrimitiveComponent*> Primitives;
	Owner->GetComponents<UPrimitiveComponent>(Primitives);

	UMaterialInterface* Override = Config.MaterialOverride.IsNull()
		? nullptr : Config.MaterialOverride.LoadSynchronous();

	for (UPrimitiveComponent* Prim : Primitives)
	{
		if (!Prim)
		{
			continue;
		}
		if (Override)
		{
			const int32 NumMats = Prim->GetNumMaterials();
			for (int32 MatIdx = 0; MatIdx < NumMats; ++MatIdx)
			{
				Prim->SetMaterial(MatIdx, Override);
			}
		}
		if (Prim->IsSimulatingPhysics() != Config.bSimulatePhysics)
		{
			Prim->SetSimulatePhysics(Config.bSimulatePhysics);
		}
	}
}

void UTemporalStateComponent::ApplyState(ETimeState State, bool bImmediate)
{
	AActor* Owner = GetOwner();
	if (!Owner)
	{
		return;
	}

	const FTransform Target = TargetTransformFor(State);
	ApplyVisualsAndPhysics(ConfigFor(State));

	if (bImmediate || BlendTime <= 0.0f)
	{
		Owner->SetActorTransform(Target, /*bSweep*/ false, nullptr, ETeleportType::TeleportPhysics);
		bBlending = false;
		SetComponentTickEnabled(false);
		return;
	}

	// Kick off a timed blend from the owner's current transform to the target.
	BlendFrom = Owner->GetActorTransform();
	BlendTo = Target;
	BlendElapsed = 0.0f;
	bBlending = true;
	SetComponentTickEnabled(true);
}

void UTemporalStateComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (!bBlending)
	{
		SetComponentTickEnabled(false);
		return;
	}

	AActor* Owner = GetOwner();
	if (!Owner)
	{
		bBlending = false;
		return;
	}

	BlendElapsed += DeltaTime;
	const float Alpha = (BlendTime > 0.0f) ? FMath::Clamp(BlendElapsed / BlendTime, 0.0f, 1.0f) : 1.0f;

	FTransform Current;
	Current.Blend(BlendFrom, BlendTo, Alpha);
	Owner->SetActorTransform(Current, /*bSweep*/ false, nullptr, ETeleportType::TeleportPhysics);

	if (Alpha >= 1.0f)
	{
		bBlending = false;
		SetComponentTickEnabled(false);
	}
}
