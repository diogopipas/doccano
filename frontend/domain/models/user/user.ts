export class UserItem {
  constructor(
    readonly id: number,
    readonly username: string,
    readonly isSuperuser: boolean,
    readonly isStaff: boolean,
    readonly email?: string,
    readonly dateJoined?: string,
    readonly lastLogin?: string
  ) {}
}
