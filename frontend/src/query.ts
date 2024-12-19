export class Query {
	packages: Set<string> = new Set();

	toUrl(): string {
		const firstItem = [...this.packages][0];
		return `api/getNetwork/${firstItem}`;
	}
}
