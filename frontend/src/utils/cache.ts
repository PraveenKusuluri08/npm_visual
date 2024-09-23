
/**
 *  Used to ensure the API isn't getting the same request too often. The backend 
 *  responses can take a while. Only let new requests in. 
 *
 *  This is a singleton since we only want one of these. 
 *
 *  This should be called every time you call the backend to get a graph, and whenever 
 *  you recieve a response. 
 */
class APICache {
  static #instance: APICache;
  private searchQueue: string[] = [];
  /**
   * Since this is a singleton, the constructor should always be private to prevent 
   * direct construction calls with the `new` operator.
   */
  private constructor() {
    console.log('apiCache created')
  }

  /**
   * The static getter that controls access to the singleton instance.
   *
   * This implementation allows you to extend the APICache class while
   * keeping just one instance of each subclass around.
   */
  public static get instance(): APICache {
    if (!APICache.#instance) {
      APICache.#instance = new APICache();
    }

    return APICache.#instance;
  }

  public addCall(url: string) {
    if (!this.searchQueue.includes(url))
      this.searchQueue.push(url);
  }

  public doesCallExist(url: string) {
    return this.searchQueue.includes(url);
  }

  public removeCall(url: string) {
    const index = this.searchQueue.indexOf(url, 0);
    if (index > -1) {
      this.searchQueue.splice(index)
    }
  }
}

export function getCache(): APICache {
  return APICache.instance;
}
