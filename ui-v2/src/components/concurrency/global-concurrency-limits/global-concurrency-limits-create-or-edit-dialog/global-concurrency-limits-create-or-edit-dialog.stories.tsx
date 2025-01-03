import {
	createFakeGlobalConcurrencyLimit,
	reactQueryDecorator,
} from "@/storybook/utils";
import type { Meta, StoryObj } from "@storybook/react";
import { GlobalConcurrencyLimitsCreateOrEditDialog } from "./global-concurrency-limits-create-or-edit-dialog";

const meta = {
	title:
		"Components/Concurrency/GlobalConcurrencyLimits/GlobalConcurrencyLimitsCreateOrEditDialog",
	component: GlobalConcurrencyLimitsCreateOrEditDialog,
	decorators: [reactQueryDecorator],
	args: {
		onOpenChange: () => {},
		onSubmit: () => {},
	},
} satisfies Meta<typeof GlobalConcurrencyLimitsCreateOrEditDialog>;

export default meta;

type Story = StoryObj<typeof GlobalConcurrencyLimitsCreateOrEditDialog>;

export const CreateLimit: Story = {};

export const EditLimit: Story = {
	args: {
		limitToUpdate: createFakeGlobalConcurrencyLimit(),
	},
};
