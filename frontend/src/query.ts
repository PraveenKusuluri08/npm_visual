export class Query {
	packages: Set<string> = new Set();

	toUrl(): string {
		const packageNames = [...this.packages].join(",");
		return `api/getNetworks/${packageNames}`;
	}
}
