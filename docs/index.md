---
hide:
  - navigation
  - toc
---

# About Ansible Molecule

Molecule project is designed to aid in the development and testing of
[Ansible](https://ansible.com) roles.

Molecule provides support for testing with multiple instances, operating
systems and distributions, virtualization providers, test frameworks and
testing scenarios.

Molecule encourages an approach that results in consistently developed
roles that are well-written, easily understood and maintained.

Molecule supports only the latest two major versions of Ansible (N/N-1).

Once installed, the command line can be called using any of the methods
below:

```bash
molecule ...
python3 -m molecule ...  # python module calling method
```

Molecule projects also hosts the [community.molecule] collection, which
contains some filters, plugins, roles and playbooks that can be used by
molecule test writers to ease writing tests.

# External Resources

Below you can see a list of useful articles and presentations, recently
updated being listed first:

- [Ansible Collections: Role Tests with
  Molecule](https://ericsysmin.com/2020/04/30/ansible-collections-role-tests-with-molecule/)
  @ericsysmin
- [Molecule v3 Slides](https://sbarnea.com/slides/molecule/#/)
  @ssbarnea.
- [Testing your Ansible roles with
  Molecule](https://www.jeffgeerling.com/blog/2018/testing-your-ansible-roles-molecule)
  @geerlingguy
- [How to test Ansible and don't go
  nuts](https://www.goncharov.xyz/it/ansible-testing-en.html)
  @ultral
