// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class game : ModuleRules
{
	public game(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate",
			"DeveloperSettings"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"game",
			"game/Variant_Platforming",
			"game/Variant_Platforming/Animation",
			"game/Variant_Combat",
			"game/Variant_Combat/AI",
			"game/Variant_Combat/Animation",
			"game/Variant_Combat/Gameplay",
			"game/Variant_Combat/Interfaces",
			"game/Variant_Combat/UI",
			"game/Variant_SideScrolling",
			"game/Variant_SideScrolling/AI",
			"game/Variant_SideScrolling/Gameplay",
			"game/Variant_SideScrolling/Interfaces",
			"game/Variant_SideScrolling/UI",
			"game/Ashfall",
			"game/Ashfall/Core",
			"game/Ashfall/Player",
			"game/Ashfall/Temporal",
			"game/Ashfall/Config"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
